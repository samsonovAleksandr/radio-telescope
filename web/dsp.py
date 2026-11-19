"""Streaming two-sided complex spectra. Full scale is 127.5 ADC counts per axis."""
import io
import math
import wave
import numpy as np

N = 2048
WINDOW = np.hanning(N)
FRAMES = 64


def samples(raw):
    a = (np.frombuffer(raw, np.uint8).astype(np.float32) - 127.5) / 127.5
    return a[::2] + 1j * a[1::2]


def analyze(path, meta, progress=lambda x: None):
    rate, center = meta["rate"], meta["center"]
    offsets = np.fft.fftshift(np.fft.fftfreq(N, 1 / rate))
    keep = (abs(offsets) < .42 * rate) & (abs(offsets) > 10000)
    total = np.zeros(N)
    size = path.stat().st_size
    if size % 2 or size < N * 2:
        raise ValueError("Нужны целые пары I/Q и хотя бы 2048 отсчётов")
    frames = clipped = 0
    # At most 600 bins regardless of observation duration.
    group = max(1, int(np.ceil((size // (2*N)) / 600)))
    sums, counts = np.zeros(600), np.zeros(600, int)
    with path.open("rb") as src:
        while raw := src.read(2*N*FRAMES):
            n = len(raw) // (2*N)
            if not n:
                break
            a = np.frombuffer(raw[:n*2*N], np.uint8)
            clipped += np.count_nonzero((a == 0) | (a == 255))
            z = samples(a).reshape(n, N)
            ps = abs(np.fft.fftshift(np.fft.fft(z * WINDOW, axis=1), axes=1))**2
            ps /= rate * np.dot(WINDOW, WINDOW)
            total += ps.sum(axis=0)
            index = np.arange(frames, frames+n) // group
            np.add.at(sums, index, ps[:, keep].sum(axis=1) * rate / N)
            np.add.at(counts, index, 1)
            frames += n
            progress(frames*N*2/size)
    active = counts > 0
    return dict(freq=(center+offsets).tolist(), valid=keep.tolist(),
                psd=(total/frames).tolist(), elapsed=frames*N/rate,
                clip=clipped/(frames*N*2), df=rate/N,
                times=((np.flatnonzero(active)*group+counts[active]/2)*N/rate).tolist(),
                power=(sums[active]/counts[active]).tolist())


def compatible(a, b):
    for key in ("profile","center","rate","gain","ppm","receiver","chain"):
        if a.get(key) != b.get(key) or a.get(key) in (None, ""):
            raise ValueError("Несовместимые или неизвестные настройки: " + key)
    if a["synthetic"] != b["synthetic"]:
        raise ValueError("Модельные и физические данные нельзя смешивать")


def wav(values, volume):
    data = (np.clip(values * volume, -1, 1) * 32767).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as out:
        out.setparams((1, 2, 32000, 0, "NONE", "not compressed"))
        out.writeframes(data.tobytes())
    return buf.getvalue()


def sound(path, meta, spec, mode, low, high, volume, start):
    rate = meta["rate"]
    lo, hi = low-meta["center"], high-meta["center"]
    if not (-.42*rate <= lo < hi <= .42*rate) or lo <= 10000 and hi >= -10000:
        raise ValueError("Выберите непрерывную полосу вне центральной маски и краёв")
    if mode == "noise":
        if not 500 <= hi-lo <= 14000:
            raise ValueError("Для переноса шума ширина полосы должна быть 0,5–14 кГц")
        # Mix at the original sample rate, isolate positive audio frequencies,
        # then interpolate the band-limited signal onto the 32 kHz audio grid.
        hop = round(rate/100)
        n = 2*hop
        clock = np.arange(n)
        frequencies = np.fft.fftfreq(n,1/rate)
        passband = (frequencies>=500) & (frequencies<=500+hi-lo)
        window = np.hanning(n+1)[:-1]
        output = np.zeros(32000*5)
        length = 0
        with path.open("rb") as f:
            f.seek(2*int(start*rate))
            prev = f.read(2*hop)
            for i in range(500):
                nxt = f.read(2*hop)
                if len(prev) != 2*hop or len(nxt) != 2*hop:
                    break
                t0 = i*hop
                mixer = np.exp(-2j*np.pi*(lo-500)*(clock+t0)/rate)
                bins = np.fft.fft(samples(prev+nxt)*mixer*window)
                block = np.fft.ifft(bins*passband).real
                first = math.ceil(t0*32000/rate)
                end = min(len(output),math.ceil((t0+n)*32000/rate))
                if first >= end:
                    break
                times = np.arange(first,end)*rate/32000-t0
                output[first:end] += np.interp(times,clock,block)
                length = end
                prev = nxt
        if not length:
            raise ValueError("С выбранного момента недостаточно IQ для звука")
        return wav(output[:length],volume)
    if mode != "spectrum":
        raise ValueError("Неизвестный режим звука")
    freq = np.array(spec["freq"])
    select = (freq >= low) & (freq <= high) & np.array(spec["valid"])
    if select.sum() < 2:
        raise ValueError("Выберите не менее двух спектральных каналов")
    t = np.arange(96000)/32000
    db = 10*np.log10(np.maximum(np.array(spec["psd"])[select],1e-20))
    level = np.interp(np.linspace(0,len(db)-1,len(t)),np.arange(len(db)),db)
    pitch = 200 + 1800*np.clip((level+120)/80,0,1)
    return wav(.45*np.sin(2*np.pi*np.cumsum(pitch)/32000),volume)
