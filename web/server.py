"""Single-instrument LAN observatory. Run one process per storage directory."""
import csv
import io
import json
import math
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import numpy as np
from dsp import analyze, compatible, sound

BASE = Path(__file__).resolve().parent
DATA = Path(os.getenv("DATA_DIR", "data")).resolve()
DATA.mkdir(parents=True, exist_ok=True)
PROFILES = {p["id"]:p for p in json.loads((BASE/"profiles.json").read_text("utf8"))}
LIMIT = int(os.getenv("MAX_UPLOAD_MIB","2048"))*1024**2
MAX_TIME = int(os.getenv("MAX_CAPTURE_SECONDS","300"))
SIM = os.getenv("SIMULATE_SDR") == "1"
RESERVE = int(os.getenv("RESERVE_MIB","128"))*1024**2
lock = threading.RLock()
jobs = {}


def save(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False),encoding="utf8")
    tmp.replace(path)


def read(path):
    return json.loads(path.read_text("utf8"))


def folder(key):
    if not re.fullmatch("[a-f0-9]{32}", key or ""):
        raise ValueError("Некорректный идентификатор")
    return DATA/key


def number(data,key,low,high,integer=False):
    x = float(data[key])
    if not math.isfinite(x) or not low <= x <= high or integer and x != int(x):
        raise ValueError("Проверьте поле " + key)
    return int(x) if integer else x


def metadata(data,source):
    profile = PROFILES[data["profile"]]
    gain = data.get("gain")
    if gain in ("",None) and source == "import":
        gain = None
    else:
        gain = number(data,"gain",0.1,49.6)
    synthetic=source=="demo" or source=="live" and SIM or source=="import" and data.get("origin")=="model"
    return dict(profile=profile["id"],name=str(data["name"])[:100] or profile["name"],
                center=number(data,"center",24000000,1766000000,True),
                rate=number(data,"rate",225001,3200000,True),gain=gain,
                ppm=number(data,"ppm",-200,200,True),role=data.get("role","ON"),
                receiver=str(data.get("receiver",""))[:100],chain=str(data.get("chain",""))[:120],
                source=source,synthetic=synthetic,
                stage="Демонстрация" if synthetic else "Эксперимент",
                created=datetime.now(timezone.utc).isoformat(),notes=str(data.get("notes",""))[:2048])


def update(job,p,phase):
    with lock:
        if job["stop"]:
            raise InterruptedError("Операция остановлена")
        job.update(progress=min(1,p),phase=phase)


def simulate(path,meta,count,progress,slow):
    rng = np.random.default_rng(208 if meta["role"]=="ON" else 412)
    n = 2048
    offsets = np.fft.fftfreq(n,1/meta["rate"])
    line = np.exp(-.5*((offsets+meta["center"]-1420405750)/32000)**2)
    shape = np.sqrt(1+line*.65*(meta["role"]=="ON" and meta["profile"]=="hydrogen"))
    with path.open("wb") as f:
        done = 0
        while done<count:
            block = min(count-done,n*40)
            rows = math.ceil(block/n)
            z = rng.standard_normal((rows,n))+1j*rng.standard_normal((rows,n))
            z = np.fft.ifft(np.fft.fft(z,axis=1)*shape,axis=1).ravel()[:block]
            scale = 21
            if meta["profile"]=="sun" and meta["role"]=="ON":
                scale *= 1+.18*np.exp(-.5*((done/count-.5)/.15)**2)
            a = np.empty(block*2,np.uint8)
            a[::2] = np.clip(np.rint(127.5+scale*z.real),0,255)
            a[1::2] = np.clip(np.rint(127.5+scale*z.imag),0,255)
            f.write(a.tobytes())
            done += block
            progress(done/count)
            if slow:
                time.sleep(block/meta["rate"])


def capture(path,meta,count,progress):
    args = ["rtl_sdr","-d","0","-f",str(meta["center"]),"-s",str(meta["rate"]),
            "-g",str(meta["gain"]),"-p",str(meta["ppm"]),"-n",str(count),str(path)]
    log = path.with_suffix(".log")
    with log.open("wb") as err:
        process = subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=err)
        deadline = time.monotonic()+count/meta["rate"]*2+15
        try:
            while process.poll() is None:
                progress(min(1,(path.stat().st_size if path.exists() else 0)/(2*count)))
                if time.monotonic()>deadline:
                    raise ValueError("SDR не поставляет данные. Проверьте USB и доступ")
                time.sleep(.15)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
    detail = log.read_text("utf8",errors="replace")
    if process.returncode or not path.exists() or path.stat().st_size != 2*count:
        raise ValueError("Сбой приёма SDR. Проверьте доступ, занятость, питание и USB. "+detail[-500:])
    actual = re.search(r"Tuner gain set to ([\d.]+)",detail)
    if actual:
        meta["gain"] = float(actual[1])


def finish(job,work):
    key = job["id"]
    staging = DATA/("partial-"+key)
    try:
        staging.mkdir()
        meta = job["meta"].copy()
        work(staging/"raw.iq",meta,lambda p:update(job,.7*p,"Получение IQ"))
        spec = analyze(staging/"raw.iq",meta,lambda p:update(job,.7+.29*p,"Усреднение спектра"))
        meta.update(id=key,bytes=(staging/"raw.iq").stat().st_size,elapsed=spec["elapsed"])
        save(staging/"spectrum.json",spec)
        save(staging/"meta.json",meta)
        with lock:
            update(job,1,"Готово")
            staging.rename(folder(key))
            job.update(state="done")
    except Exception as exc:
        with lock:
            job.update(state="stopped" if job["stop"] else "error",
                       phase="Остановлено" if job["stop"] else str(exc))
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def begin(data,source,size):
    meta = metadata(data,source)
    with lock:
        if any(j["state"]=="running" for j in jobs.values()):
            raise ValueError("Идёт другая операция. Дождитесь завершения или остановите её")
        if size+RESERVE>shutil.disk_usage(DATA).free:
            raise ValueError("Недостаточно места с учётом резерва")
        key = str(data.get("id",uuid.uuid4().hex))
        folder(key)
        if key in jobs or folder(key).exists():
            raise ValueError("Этот идентификатор уже используется")
        for old in list(jobs)[:-30]:
            del jobs[old]
        job = dict(id=key,state="running",progress=0,phase="Подготовка",stop=False,meta=meta)
        jobs[key] = job
        return job


def result(key,ref):
    meta = read(folder(key)/"meta.json")
    spec = read(folder(key)/"spectrum.json")
    vals = np.array(spec["psd"])
    unit = "дБFS/Гц"
    if ref:
        other = read(folder(ref)/"meta.json")
        compatible(meta,other)
        off = read(folder(ref)/"spectrum.json")
        if spec["freq"] != off["freq"] or spec["valid"] != off["valid"]:
            raise ValueError("Частотные сетки различаются")
        den = np.array(off["psd"])
        vals = 100*(np.divide(vals,den,out=np.full_like(vals,np.nan),where=den>0)-1)
        unit = "100 × (ON/OFF − 1), %"
    else:
        vals = 10*np.log10(np.maximum(vals,1e-30))
    values = [v if valid and math.isfinite(v) else None for v,valid in zip(vals.tolist(),spec["valid"])]
    return dict(meta=meta,freq=spec["freq"],values=values,unit=unit,df=spec["df"],
                times=spec["times"],power=spec["power"],clip=spec["clip"],
                offPower=off["power"] if ref else [],offTimes=off["times"] if ref else [])


def device():
    if SIM:
        return "Имитатор SDR"
    if not shutil.which("rtl_eeprom"):
        return "Утилиты RTL-SDR отсутствуют"
    try:
        proc = subprocess.run(["rtl_eeprom","-d","0"],capture_output=True,timeout=4)
        detail=(proc.stdout+proc.stderr).decode(errors="replace")
        if "usb_claim_interface" in detail or "busy" in detail.lower():
            return "SDR занят другим процессом или драйвером DVB"
        if "permission" in detail.lower() or "usb_open error -3" in detail:
            return "Доступ к USB запрещён"
        if proc.returncode:
            return "SDR недоступен. Проверьте USB и права"
        return "SDR доступен"
    except (OSError, subprocess.TimeoutExpired):
        return "SDR не ответил"


class Handler(BaseHTTPRequestHandler):
    def reply(self,body,kind="application/json; charset=utf-8",status=200):
        if not isinstance(body,bytes):
            body = json.dumps(body,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type",kind)
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self):
        url=urlsplit(self.path)
        q={k:v[-1] for k,v in parse_qs(url.query).items()}
        path=url.path
        post=self.command=="POST"
        if post:
            origin=self.headers.get("Origin")
            if origin and urlsplit(origin).netloc != self.headers.get("Host"):
                raise ValueError("Недопустимый источник запроса")
            size=int(self.headers.get("Content-Length","0"))
            if path!="/api/import" and not 0<=size<=16384:
                raise ValueError("Слишком большой запрос")
            data={} if path=="/api/import" or not size else json.loads(self.rfile.read(size))
        if not post and path in ("/","/app.js","/style.css"):
            file=BASE/"static"/("index.html" if path=="/" else path[1:])
            return self.reply(file.read_bytes(),{".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".css":"text/css"}[file.suffix])
        if path=="/api/state" and not post:
            with lock:
                active=next((j["id"] for j in jobs.values() if j["state"]=="running"),None)
                settings=read(DATA/"settings.json") if (DATA/"settings.json").exists() else {}
            records=sorted((read(p) for p in DATA.glob("[0-9a-f]"*32+"/meta.json")),key=lambda m:m["created"],reverse=True)
            return self.reply(dict(profiles=list(PROFILES.values()),records=records,active=active,
                                   free=shutil.disk_usage(DATA).free,settings=settings,limit=LIMIT,maxTime=MAX_TIME))
        if path=="/api/device" and not post:
            with lock:
                busy=any(j["state"]=="running" and j["meta"]["source"]=="live" for j in jobs.values())
            return self.reply({"message":"SDR занят записью" if busy else device()})
        if path=="/api/confirm" and post:
            with lock:
                main=folder(data["id"])/"meta.json"
                a,b=read(main),read(folder(data["repeat"])/"meta.json")
                if a["synthetic"] or b["synthetic"] or a["profile"]!=b["profile"] or a["center"]==b["center"]:
                    raise ValueError("Нужны две физические записи одного профиля с разными центрами настройки")
                evidence=str(data["evidence"]).strip()
                if len(evidence)<20:
                    raise ValueError("Опишите результаты измерений и критерий повторяемости")
                a.update(stage="Подтверждено наблюдателем",repeat=b["id"],evidence=evidence[:4096])
                save(main,a)
            return self.reply({})
        if path=="/api/settings" and post:
            with lock:
                save(DATA/"settings.json",{k:data[k] for k in ("profile","volume") if k in data})
            return self.reply({})
        if path=="/api/start" and post:
            source=data["source"]
            if source not in ("demo","live"):
                raise ValueError("Неизвестный источник")
            seconds=number(data,"seconds",.1,MAX_TIME)
            count=int(number(data,"rate",225001,3200000,True)*seconds)
            def work(p,m,cb):
                if source=="demo" or SIM:
                    simulate(p,m,count,cb,source=="live")
                else:
                    capture(p,m,count,cb)
            job=begin(data,source,count*2)
            threading.Thread(target=finish,args=(job,work),daemon=True).start()
            return self.reply({"id":job["id"]})
        if path=="/api/import" and post:
            if not 4096<=size<=LIMIT or size%2:
                raise ValueError("Файл должен укладываться в лимит и содержать целые пары IQ")
            job=begin(q,"import",size)
            def upload(p,m,cb):
                left=size
                self.connection.settimeout(15)
                with p.open("wb") as f:
                    while left:
                        block=self.rfile.read(min(left,262144))
                        if not block:
                            raise ValueError("Передача прервана")
                        f.write(block)
                        left-=len(block)
                        cb(1-left/size)
            finish(job,upload)
            return self.reply({"id":job["id"]})
        if path=="/api/job":
            with lock:
                job=jobs[(data if post else q)["id"]]
                if post:
                    job["stop"]=True
                return self.reply({k:job[k] for k in ("id","state","phase","progress")})
        if path in ("/api/result","/api/csv") and not post:
            res=result(q["id"],q.get("off"))
            if path.endswith("csv"):
                buf=io.StringIO()
                writer=csv.writer(buf)
                if PROFILES[res["meta"]["profile"]]["view"]=="time":
                    writer.writerow(["record","seconds","power_FS_squared"])
                    for label,x,y in [("primary",res["times"],res["power"]),("reference",res["offTimes"],res["offPower"])]:
                        writer.writerows((label,t,p) for t,p in zip(x,y))
                    return self.reply(buf.getvalue().encode("utf-8-sig"),"text/csv; charset=utf-8")
                writer.writerow(["RF_Hz",res["unit"],"valid"])
                writer.writerows((f,v,int(v is not None)) for f,v in zip(res["freq"],res["values"]))
                return self.reply(buf.getvalue().encode("utf-8-sig"),"text/csv; charset=utf-8")
            return self.reply(res)
        if path in ("/api/meta","/api/audio") and not post:
            d=folder(q["id"])
            m=read(d/"meta.json")
            if path.endswith("meta"):
                return self.reply(m)
            audio=sound(d/"raw.iq",m,read(d/"spectrum.json"),q["mode"],float(q["lo"]),float(q["hi"]),
                        number(q,"volume",0,4),number(q,"start",0,m["elapsed"]))
            return self.reply(audio,"audio/wav")
        self.reply({"error":"Страница отсутствует"},status=404)

    def handle_request(self):
        try:
            self.dispatch()
        except (BrokenPipeError,ConnectionResetError):
            pass
        except (ValueError,KeyError,OSError,TypeError) as exc:
            self.reply({"error":str(exc)},status=400)
    do_GET = do_POST = handle_request


if __name__=="__main__":
    for partial in DATA.glob("partial-*"):
        if re.fullmatch("partial-[a-f0-9]{32}",partial.name) and partial.is_dir():
            shutil.rmtree(partial)
    ThreadingHTTPServer((os.getenv("BIND","0.0.0.0"),int(os.getenv("PORT","8080"))),Handler).serve_forever()
