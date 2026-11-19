"""Run with python -m unittest discover -s tests from the project root."""
import io
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"web"))
from dsp import N, analyze, compatible, sound
from server import simulate


class SpectralTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"sample.iq"
        self.meta=dict(rate=2400000,center=1420000000,profile="hydrogen",role="ON",
                       gain=28,ppm=0,receiver="V3",chain="LNA",synthetic=True)

    def test_frequency_power_masks_and_audio(self):
        rate=self.meta["rate"]
        k=np.arange(rate//8)
        # 300 kHz complex tone is exactly FFT channel +256.
        z=40*np.exp(2j*np.pi*k/8)
        raw=np.stack((z.real,z.imag),axis=1)
        np.clip(np.rint(raw+127.5),0,255).astype(np.uint8).tofile(self.path)
        s=analyze(self.path,self.meta)
        self.assertEqual(s["freq"][np.argmax(s["psd"])],1420300000)
        self.assertAlmostEqual(sum(s["psd"])*s["df"],(40/127.5)**2,delta=.003)
        self.assertFalse(s["valid"][N//2] or s["valid"][0])
        audio=sound(self.path,self.meta,s,"noise",1420298500,1420303500,1,0)
        with wave.open(io.BytesIO(audio)) as w:
            a=np.frombuffer(w.readframes(w.getnframes()),"<i2")[320:-320]
        hz=np.argmax(abs(np.fft.rfft(a*np.hanning(len(a)))))*32000/len(a)
        self.assertAlmostEqual(hz,2000,delta=12)

    def test_line_width_recovery_and_retune(self):
        for center in (1420000000,1420800000):
            m=dict(self.meta,center=center)
            spectra=[]
            for role in ("ON","OFF"):
                simulate(self.path,dict(m,role=role),2400000,lambda _:None,False)
                spectra.append(analyze(self.path,m))
            f=np.array(spectra[0]["freq"])
            excess=np.array(spectra[0]["psd"])/spectra[1]["psd"]-1
            def band(offset):
                return excess[abs(f-1420405750-offset)<10000].mean()
            self.assertAlmostEqual(band(0),.65,delta=.07)
            self.assertAlmostEqual(band(32000),.65*np.exp(-.5),delta=.08)
            self.assertAlmostEqual(band(140000),0,delta=.06)

    def test_matching_and_input_validation(self):
        for key,val in [("gain",35),("center",1420800000),("rate",2048000),("chain",""),
                        ("ppm",1),("profile","sun"),("synthetic",False),("receiver","V4")]:
            with self.assertRaises(ValueError):
                compatible(self.meta,dict(self.meta,**{key:val}))
        for size in (3,2048,4097):
            self.path.write_bytes(bytes(size))
            with self.assertRaises(ValueError):
                analyze(self.path,self.meta)
