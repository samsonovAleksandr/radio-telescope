"""Compare two rtl_sdr unsigned 8-bit interleaved IQ files."""
import argparse

import numpy as np


def spectrum(path, size=1024):
    window = np.hanning(size)
    total = np.zeros(size)
    frames = 0
    with open(path, "rb") as source:
        while raw := source.read(2 * size * 256):
            count = len(raw) // (2 * size)
            if not count:
                break
            iq = np.frombuffer(raw[:2 * size * count], np.uint8).astype(np.float32) - 127.5
            samples = (iq[::2] + 1j * iq[1::2]).reshape(count, size)
            total += (abs(np.fft.fft(samples * window, axis=1)) ** 2).sum(axis=0)
            frames += count
    if not frames or not total.all():
        raise ValueError(f"Недостаточно данных или пустые каналы в {path}")
    return np.fft.fftshift(total / frames)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("on")
    parser.add_argument("off")
    parser.add_argument("--center", type=float, default=1420000000)
    parser.add_argument("--rate", type=float, default=2400000)
    parser.add_argument("--out", default="spectrum.csv")
    args = parser.parse_args()
    excess = spectrum(args.on) / spectrum(args.off) - 1
    offsets = np.fft.fftshift(np.fft.fftfreq(len(excess), 1 / args.rate))
    keep = (abs(offsets) < 0.42 * args.rate) & (abs(offsets) > 10000)
    result = np.column_stack(((args.center + offsets[keep]) / 1e6, 100 * excess[keep]))
    np.savetxt(args.out, result, delimiter=",", header="MHz,excess_percent", comments="")
