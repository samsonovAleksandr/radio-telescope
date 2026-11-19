"""Checks against a disposable default container without a USB device."""
import argparse
import csv
import io
import json
import time
import urllib.error
import urllib.request

def run(base):
    def request(path,data=None,raw=False):
        body=json.dumps(data).encode() if data is not None else None
        with urllib.request.urlopen(base+"/api/"+path,body,timeout=20) as r:
            payload=r.read()
            return payload if raw else json.loads(payload)
    def complete(m):
        key=request("start",m)["id"]
        for _ in range(200):
            job=request("job?id="+key)
            if job["state"]!="running":
                return job
            time.sleep(.1)
        raise AssertionError("capture timeout")
    print("USB:",request("device")["message"])
    meta=dict(profile="sun",name="QA солнечный проход",seconds=1,center=1420000000,
              rate=2400000,receiver="V3",chain="test",ppm=0,gain=28,role="ON",source="demo")
    on=complete(meta)
    off=complete(dict(meta,role="OFF"))
    assert on["state"]==off["state"]=="done"
    suffix="?id="+on["id"]+"&off="+off["id"]
    res=request("result"+suffix)
    peak=res["power"][len(res["power"])//2]/res["offPower"][len(res["offPower"])//2]
    assert 1.2<peak<1.7,peak
    rows=list(csv.reader(io.StringIO(request("csv"+suffix,raw=True).decode("utf-8-sig"))))
    assert rows[0][1]=="seconds" and rows[-1][0]=="reference"
    print("PASS solar time series, common power scale, CSV",round(peak,3))
    incompatible=complete(dict(meta,center=1420800000))
    try:
        request("result?id="+on["id"]+"&off="+incompatible["id"])
    except urllib.error.HTTPError as e:
        assert e.code==400 and "center" in e.read().decode()
    else:
        raise AssertionError("incompatible grids accepted")
    try:
        request("confirm",dict(id=on["id"],repeat=incompatible["id"],evidence="Модельное подтверждение должно отклоняться"))
    except urllib.error.HTTPError as e:
        assert e.code==400
    else:
        raise AssertionError("demo could be confirmed")
    failed=complete(dict(meta,source="live"))
    assert failed["state"]=="error",failed
    assert all(r["id"]!=failed["id"] for r in request("state")["records"])
    request("settings",{"profile":"hydrogen","volume":"0.65"})
    assert request("state")["settings"]["volume"]=="0.65"
    print("PASS mismatch rejection, evidence guard, real capture error without USB, saved settings")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url",nargs="?",default="http://127.0.0.1:18080")
    run(parser.parse_args().url.rstrip("/"))
