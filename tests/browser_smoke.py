"""Browser smoke test for a disposable simulated instance. Run with URL argument."""
import argparse
import csv
import io
import json
import math
import os
import struct
import tempfile
import uuid
import wave
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def check_ui(page, base, directory):
    prefix = "QA-" + uuid.uuid4().hex[:7]
    page.goto(base)
    expect(page.locator("#profile")).to_have_value("hydrogen")
    expect(page.locator("#disk")).not_to_be_empty()
    select = lambda control, value: page.locator("#" + control).select_option(value)
    field = lambda control, value: page.locator("#" + control).fill(str(value))
    click = lambda control: page.locator("#" + control).click()

    def acquire(source, role, name, duration=0.6):
        select("source", source)
        select("role", role)
        field("name", prefix + name)
        if source != "import":
            field("seconds", duration)
        click("start")
        item = page.locator("#record option").filter(has_text=prefix + name)
        expect(item).to_have_count(1, timeout=45000)
        selected = item.get_attribute("value")
        expect(page.locator("#start")).to_be_enabled()
        expect(page.locator("#record")).to_have_value(selected)
        return selected

    def download(selector, suffix):
        with page.expect_download() as event:
            page.locator(selector).first.click()
        target = directory / ("download." + suffix)
        event.value.save_as(target)
        return target.read_bytes()

    on = acquire("demo", "ON", "-line")
    off = acquire("demo", "OFF", "-reference")
    with page.expect_response(lambda response: "/api/result?" in response.url and on in response.url):
        select("record", on)
    select("off", off)
    expect(page.locator("#stage")).to_contain_text("Демонстрац")
    payload = download("#csv", "csv")
    reader = csv.reader(io.StringIO(payload.decode("utf-8-sig")))
    header = next(reader)
    assert header[0] == "RF_Hz" and "%" in header[1], header
    spectrum = [(float(row[0]),float(row[1]) if row[1] else None) for row in reader]
    assert len(spectrum) == 2048 and spectrum[len(spectrum)//2][1] is None
    assert spectrum[0][1] is None and spectrum[-1][1] is None
    def average(low,high):
        values = [v for f,v in spectrum if low <= f < high and v is not None]
        return sum(values)/len(values)
    peak = average(1420385750,1420425750)
    continuum = average(1420520000,1420700000)
    assert 35 < peak - continuum < 100, (peak,continuum)
    png = download("#png","png")
    assert png[:8] == bytes.fromhex("89504e470d0a1a0a") and len(png)>5000
    assert min(struct.unpack(">II",png[16:24])) > 100
    meta = json.loads(download("#metadata","json"))
    assert meta["synthetic"] and meta["id"] == on, meta
    plot = page.locator("#plot")
    plot.hover(position={"x":220,"y":150})
    expect(page.locator("#cursor")).not_to_have_text("Курсор на графике · колесо для масштаба")
    page.mouse.wheel(0,-230)
    click("reset")
    print(f"PASS demo ON/OFF, masks, line {peak:.1f}%, continuum {continuum:.1f}%, cursor, wheel, CSV/PNG/JSON")
    for mode in ("noise","spectrum"):
        select("mode",mode)
        field("lo",1420.400)
        field("hi",1420.409)
        click("listen")
        players = page.locator("#players audio")
        expect(players).to_have_count(2)
        player = players.first
        page.wait_for_function("document.querySelector('#players audio')?.readyState >= 2")
        player.evaluate("(el) => el.play()")
        page.wait_for_function("document.querySelector('#players audio').currentTime > 0")
        player.evaluate("(el) => el.pause()")
        sample = download("#players a[download]","wav")
        with wave.open(io.BytesIO(sample)) as wav:
            assert wav.getframerate()==32000 and wav.getnchannels()==1 and wav.getsampwidth()==2
            assert wav.getnframes()>1000
        print(f"PASS {mode}: two players, playback clock advances, PCM WAV download")
    raw = directory / "test.iq"
    # Exactly 1/8 of sample rate, corresponding to +300 kHz at 2.4 Msps.
    period = bytes(v for k in range(8) for v in (
        round(127.5+50*math.cos(k*math.pi/4)),round(127.5+50*math.sin(k*math.pi/4))))
    raw.write_bytes(period*8192)
    select("source","import")
    page.locator("#file").set_input_files(str(raw))
    imported = acquire("import","ON","-import")
    select("off","")
    expect(page.locator("#stage")).to_contain_text("Эксперимент")
    single = csv.reader(io.StringIO(download("#csv","csv").decode("utf-8-sig")))
    next(single)
    f, value = max(((float(row[0]),float(row[1])) for row in single if row[1]), key=lambda r:r[1])
    assert abs(f-1420300000) < 1172, (f, value)
    select("source","live")
    click("probe")
    expect(page.locator("#device")).to_contain_text("Имитатор")
    live = acquire("live","ON","-sim",0.4)
    assert live != imported
    expect(page.locator("#stage")).to_contain_text("Демонстрац")
    field("seconds",15)
    field("name",prefix+"-cancel")
    click("start")
    expect(page.locator("#start")).to_be_disabled()
    expect(page.locator("#jobbox")).to_be_visible()
    click("stop")
    page.wait_for_function("document.querySelector('#jobbox').hidden || document.querySelector('#phase').textContent.includes('Останов')", timeout=30000)
    page.reload()
    expect(page.locator("#record option").filter(has_text=prefix+"-sim")).to_have_count(1)
    expect(page.locator("#record option").filter(has_text=prefix+"-cancel")).to_have_count(0)
    print("PASS imported CU8 tone, simulated USB capture, explicit synthetic origin, cancelled record absent after reload")
    select("source","import")
    sidecar = directory / "demo-meta.json"
    sidecar.write_text(json.dumps(meta),encoding="utf8")
    page.locator("#sidecar").set_input_files(str(sidecar))
    expect(page.locator("#origin")).to_have_value("model")
    expect(page.locator("#center")).to_have_value("1420")
    page.locator("#file").set_input_files(str(raw))
    field("name",prefix+"-sidecar")
    click("start")
    expect(page.locator("#record option").filter(has_text=prefix+"-sidecar")).to_have_count(1)
    expect(page.locator("#stage")).to_contain_text("Демонстрац")
    print("PASS optional JSON sidecar and retained model provenance")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url",nargs="?",default="http://127.0.0.1:18080")
    parser.add_argument("--browser",default=os.getenv("CHROME_PATH"),help="Path to an existing Chromium or Chrome executable")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser,headless=True)
        page = browser.new_page(viewport={"width":1300,"height":920},accept_downloads=True)
        page.set_default_timeout(12000)
        errors = []
        page.on("pageerror",lambda exc: errors.append(str(exc)))
        try:
            check_ui(page,args.url,Path(tmp))
            assert not errors, errors
        except Exception:
            print("UI error:",page.locator("#error").inner_text(timeout=2000))
            print("JavaScript errors:",errors)
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()
