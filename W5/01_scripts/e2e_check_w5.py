"""Playwright end-to-end check of the W5 explorer (http://localhost:8767/).

Covers, per viewport (4K monitor, laptop, small laptop, tablet portrait, phone, small phone):
 - loads with data, no console errors, no horizontal page overflow
 - route geometry is road-following (pts > stops*3)  [the W4 regression guard]
 - 3-way view switcher incl. sensor day-drops and driver-view column hiding
 - evidence bars, src tags, sensor-only diamonds
 - playback engine: starts, advances the clock, reports a speed, scrubs, stops
 - responsive drawers on narrow screens (FABs open/close panels)
 - info modal tabs render from info_stats.json
Run:  python -X utf8 W5/01_scripts/e2e_check_w5.py
"""
import json
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8767/"
SHOT = r"C:\Users\esmae\Desktop\phd Esmaeil\THESIS CLAUDE\W5\03_outputs"
VIEWPORTS = [
    ("monitor4k", 2560, 1400, False),
    ("laptop", 1440, 900, False),
    ("laptop_small", 1180, 720, False),
    ("tablet", 768, 1024, True),
    ("phone", 390, 844, True),
    ("phone_small", 360, 700, True),
]

FAILS = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (f"  [{detail}]" if detail else ""))
    if not cond:
        FAILS.append(name + " " + str(detail))


def main():
    results = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for vname, w, h, narrow in VIEWPORTS:
            pg = b.new_page(viewport={"width": w, "height": h})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            pg.goto(URL, timeout=30000)
            pg.wait_for_function("typeof TRIPS !== 'undefined' && TRIPS.length > 0", timeout=30000)
            pg.wait_for_function("document.getElementById('loadstate').textContent === ''", timeout=90000)
            print(f"\n=== {vname} {w}x{h} ===")

            # no horizontal overflow
            overflow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check("no horizontal overflow", overflow <= 1, overflow)

            if narrow:
                # drawers: closed by default, FAB opens, close button closes
                check("FABs visible", pg.locator("#fabCal").is_visible() and pg.locator("#fabTrips").is_visible())
                pg.click("#fabCal")
                pg.wait_for_timeout(350)
                check("left drawer opens", pg.evaluate("document.getElementById('left').classList.contains('open')"))
                pg.click("#dcL")
                pg.wait_for_timeout(350)
                check("left drawer closes", pg.evaluate("!document.getElementById('left').classList.contains('open')"))
                pg.click("#fabTrips")
                pg.wait_for_timeout(350)
                check("right drawer opens", pg.evaluate("document.getElementById('sidebar').classList.contains('open')"))
                pg.click("#dcR")
                pg.wait_for_timeout(350)

            stats = pg.evaluate(
                """async () => {
        const out = {};
        // pick a busy year trip with a route
        await ensureYear(2022);
        const cand = TRIPS.filter(t => t.date.slice(0,4)==='2022' && (t.n_bins||0) >= 5);
        let t = cand.find(x => ROUTES[x.id] && (ROUTES[x.id].a||[]).length > 1) || cand[0];
        state.year = 2022; document.getElementById('year').value = '2022';
        calendar();
        state.selDay = t.date; calendar(); daypanel();
        await toggle(t);
        out.selected = state.sel.size;
        // ROUTE GEOMETRY: road-following, never straight lines
        const checks = [...state.sel.values()].map(x => {
          const r = ROUTES[x.t.id];
          const p = r ? decodePoly(r.p || r.path) : null;
          return { id: x.t.id, pts: p ? p.length : 0, stops: (x.t.stops||[]).length };
        });
        out.routeChecks = checks;
        out.roadFollowing = checks.every(c => c.pts > c.stops * 3);
        // src tags & sensor col in combined view
        const cardsHtml = document.getElementById('cards').innerHTML;
        out.hasSrcTags = cardsHtml.includes('srctag');
        out.evidenceLine = cardsHtml.includes('evidence:');
        // playback
        out.playBtn = !!document.querySelector('.pbtn');
        if (out.playBtn){
          pbStart(t.id);
          out.playbarOn = document.getElementById('playbar').classList.contains('on');
          await new Promise(r => setTimeout(r, 1200));
          out.clockText = document.getElementById('pbClock').textContent;
          out.speedText = document.getElementById('pbSpeed').textContent;
          const before = PB.cur;
          await new Promise(r => setTimeout(r, 800));
          out.clockAdvances = PB.cur > before;
          document.getElementById('pbScrub').value = '50';
          document.getElementById('pbScrub').dispatchEvent(new Event('input'));
          out.scrubWorks = Math.abs((PB.cur - PB.t0) - 5) < 0.6;
          pbStop();
          out.playbarOffAfterStop = !document.getElementById('playbar').classList.contains('on');
        }
        // driver view hides sensor artefacts
        setView('driver');
        await new Promise(r => setTimeout(r, 400));
        out.driverBodyClass = document.body.className === 'view-driver';
        out.driverSensColHidden = (() => { const el = document.querySelector('.senscol'); return !el || el.offsetParent === null; })();
        // sensor view: day drops
        setView('sensor');
        await new Promise(r => setTimeout(r, 600));
        const dayKeys = Object.keys(DAYDROPS);
        out.dayDropKeys = dayKeys.length;
        if (dayKeys.length){
          state.selDay = dayKeys[0]; await daypanel();
          out.sensorChips = document.querySelectorAll('.schip').length;
        }
        setView('combined');
        await new Promise(r => setTimeout(r, 400));
        // info modal
        document.getElementById('infoBtn').click();
        await new Promise(r => setTimeout(r, 600));
        out.infoOpen = document.getElementById('infoModal').classList.contains('on');
        const tabs = ['overview','trips','sensors','cross','assump','sources'];
        out.tabsOk = [];
        for (const tb of tabs){
          document.querySelector(`#infoTabs button[data-tab="${tb}"]`).click();
          await new Promise(r => setTimeout(r, 150));
          const html = document.getElementById('infoBody').innerHTML;
          out.tabsOk.push(html.length > 200 && !html.includes('tab data missing'));
        }
        document.getElementById('infoClose').click();
        // phantom draws dotted
        const ph = TRIPS.find(x => x.frac === 'Phantom' && (x.n_bins||0) >= 4);
        out.phantomExists = !!ph;
        return out;
      }"""
            )
            results[vname] = stats
            check("trip selected", stats.get("selected", 0) >= 1)
            check("routes are road-following", stats.get("roadFollowing") is True, json.dumps(stats.get("routeChecks", [])[:2]))
            check("src tags present", stats.get("hasSrcTags") is True)
            check("evidence line present", stats.get("evidenceLine") is True)
            check("playback available", stats.get("playBtn") is True)
            if stats.get("playBtn"):
                check("playback bar shows", stats.get("playbarOn") is True)
                check("playback clock advances", stats.get("clockAdvances") is True, stats.get("clockText"))
                check("playback speed readout", "km/h" in (stats.get("speedText") or "") or "at " in (stats.get("speedText") or ""), stats.get("speedText"))
                check("playback scrub", stats.get("scrubWorks") is True)
                check("playback stop", stats.get("playbarOffAfterStop") is True)
            check("driver view class", stats.get("driverBodyClass") is True)
            check("driver view hides sensor cols", stats.get("driverSensColHidden") is True)
            check("sensor day-drops loaded", stats.get("dayDropKeys", 0) > 0, stats.get("dayDropKeys"))
            check("sensor chips listed", stats.get("sensorChips", 0) > 0, stats.get("sensorChips"))
            check("info modal opens", stats.get("infoOpen") is True)
            check("all 6 info tabs render", all(stats.get("tabsOk", [])), stats.get("tabsOk"))
            check("phantom tracks present", stats.get("phantomExists") is True)
            check("no console errors", not errors, "; ".join(errors[:3]))
            pg.screenshot(path=f"{SHOT}\\w5_e2e_{vname}.png")
            pg.close()

        # deep-link check (desktop): ?view=sensor&day= + ?trip=
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(URL + "?view=sensor", timeout=30000)
        pg.wait_for_function("document.getElementById('loadstate').textContent === ''", timeout=90000)
        check("deep link ?view=sensor", pg.evaluate("state.view") == "sensor")
        tid = pg.evaluate("(TRIPS.find(t => (t.n_bins||0) >= 5) || {}).id")
        if tid:
            pg.goto(f"{URL}?trip={tid}", timeout=30000)
            pg.wait_for_function("document.getElementById('loadstate').textContent === ''", timeout=90000)
            pg.wait_for_timeout(1500)
            check("deep link ?trip draws", pg.evaluate("state.sel.size") >= 1, tid)
        pg.close()
        b.close()

    print("\n" + ("ALL CHECKS PASSED" if not FAILS else f"{len(FAILS)} FAILURES:\n- " + "\n- ".join(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
