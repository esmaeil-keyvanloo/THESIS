"""W2 - Report figures (light mode, reference palette, mark specs per dataviz method)."""
import duckdb, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = f"{BASE}/W2/03_outputs/figures"
os.makedirs(OUT, exist_ok=True)

# palette / chrome (reference instance, light mode)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CRIT = "#d03b3b"
SURF, INK, INK2, MUTED, GRID, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 9,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
    "axes.edgecolor": BASELINE, "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "text.color": INK, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False,
})

con = duckdb.connect()
norm = """
    trim(idcontentor) AS cid, trim(description) AS fraction,
    TRY_CAST("Enchimento" AS INT) AS fill, trim(idrecolha) AS idr,
    TRY_CAST("Data de \u00ednicio" AS TIMESTAMP) AS t_start,
    TRY_CAST("Data da leitura" AS TIMESTAMP) AS ts
"""
con.sql(f"CREATE VIEW c AS SELECT {norm} FROM '{BASE}/Brain/03_db/parquet/raw_collections.parquet'")
con.sql(f"CREATE VIEW s AS SELECT {norm} FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet'")
V = json.load(open(f"{BASE}/W2/02_data_work/codex_verification.json", encoding="utf-8"))

def style(ax):
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=200, bbox_inches="tight", facecolor=SURF)
    plt.close(fig)
    print("wrote", name)

# ---- F1: monthly rows by source, partial 2024 flagged ----
m = con.sql("""
  SELECT date_trunc('month', ts) ym,
    SUM(CASE WHEN src='driver' THEN 1 ELSE 0 END) driver,
    SUM(CASE WHEN src='sensor' THEN 1 ELSE 0 END) sensor
  FROM (SELECT ts, 'driver' src FROM c UNION ALL SELECT ts, 'sensor' src FROM s)
  GROUP BY 1 ORDER BY 1
""").df()
fig, ax = plt.subplots(figsize=(7.4, 2.9))
ax.axvspan(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-04-30"), color=GRID, alpha=0.5, lw=0)
ax.plot(m.ym, m.sensor, color=BLUE, lw=2, label="Sensor readings")
ax.plot(m.ym, m.driver, color=ORANGE, lw=2, label="Driver records")
ax.set_title("Monthly record volume by source, 2020\u20132024")
ax.set_ylabel("rows / month")
ax.legend(loc="upper left", ncol=2)
ax.annotate("2024:\nJan\u2013Apr only", xy=(pd.Timestamp("2024-02-20"), m.sensor.max()*0.72),
            fontsize=8, color=INK2, ha="center")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_ylim(0)
style(ax); ax.grid(axis="y")
save(fig, "F1_monthly_volume")

# ---- F2: fill distributions, two panels ----
drv = con.sql("SELECT fill, COUNT(*) n FROM c WHERE fill IS NOT NULL GROUP BY 1 ORDER BY 1").df()
sen = con.sql("SELECT CASE WHEN fill<0 THEN -10 ELSE (fill//10)*10 END b, COUNT(*) n FROM s GROUP BY 1 ORDER BY 1").df()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.9))
vals = [-1, 0, 25, 50, 75, 100]
d = {r.fill: r.n/1000 for r in drv.itertuples()}
cols = [CRIT if v == -1 else ORANGE for v in vals]
a1.bar(range(len(vals)), [d.get(v, 0) for v in vals], color=cols, width=0.55)
a1.set_xticks(range(len(vals)), ["\u22121", "0", "25", "50", "75", "100"])
a1.set_title("Driver: four-point scale + zero")
a1.set_ylabel("rows (thousands)")
for i, v in enumerate(vals):
    a1.text(i, d.get(v, 0)+3, f"{d.get(v,0):.0f}k", ha="center", fontsize=7.5, color=INK2)
sb = {r.b: r.n/1000 for r in sen.itertuples()}
xs = sorted(sb)
a2.bar(range(len(xs)), [sb[x] for x in xs], color=[CRIT if x < 0 else BLUE for x in xs], width=0.62)
a2.set_xticks(range(len(xs)), ["neg"] + [str(x) for x in xs if x >= 0])
a2.set_title("Sensor: near-continuous, ceiling 82\u201384")
for a in (a1, a2):
    style(a); a.grid(axis="y")
save(fig, "F2_fill_distributions")

# ---- F3: anatomy of driver zeros ----
Z = V["zeros"]
fig, ax = plt.subplots(figsize=(7.4, 2.5))
rows = [
    ("All zero rows", Z["total_zero_rows"], MUTED),
    ("Paired: another reading \u226415 min before", Z["zeros_with_reading_within_15min_before"], ORANGE),
    ("   of which previous reading nonzero\n   (post-emptying confirmations)", Z["of_which_previous_nonzero"], CRIT),
    ("Standalone zeros (no nearby reading)", Z["standalone_zeros"], BLUE),
]
ys = range(len(rows))[::-1]
ax.barh(list(ys), [r[1] for r in rows], color=[r[2] for r in rows], height=0.5)
ax.set_yticks(list(ys), [r[0] for r in rows], fontsize=8.5)
for y, r in zip(ys, rows):
    ax.text(r[1]+2000, y, f"{r[1]:,}", va="center", fontsize=8, color=INK2)
ax.set_title("What the 144,804 driver zeros actually are")
ax.set_xlim(0, Z["total_zero_rows"]*1.18)
ax.grid(axis="x"); ax.grid(axis="y", visible=False); ax.tick_params(length=0)
save(fig, "F3_zero_anatomy")

# ---- F4: active windows + cadence ----
aw = pd.read_csv(f"{BASE}/W2/02_data_work/sensor_active_windows.csv")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.9), width_ratios=[3, 2])
a1.hist(aw.active_days, bins=30, color=BLUE)
a1.set_title("Per-container active window (days)")
a1.set_ylabel("containers")
a1.axvline(365, color=CRIT, lw=1.2, ls="--")
a1.text(365, a1.get_ylim()[1]*0.9, " 64 containers < 1 year", fontsize=8, color=CRIT)
style(a1); a1.grid(axis="y")
rates = [("Calendar\nwindow", 1.93, MUTED),
         ("Days with\n\u22651 reading", 2.55, BLUE),
         ("Within own\nactive window", 1.58, AQUA)]
a2.bar(range(3), [r[1] for r in rates], color=[r[2] for r in rates], width=0.5)
a2.set_xticks(range(3), [r[0] for r in rates], fontsize=7.5)
for i, r in enumerate(rates):
    a2.text(i, r[1]+0.06, f"{r[1]:.2f}", ha="center", fontsize=9, fontweight="bold", color=INK)
a2.set_title("Readings per container-day:\nthree denominators")
style(a2); a2.grid(axis="y")
save(fig, "F4_cadence_windows")

# ---- F5: collection start hours (shift structure) ----
h = con.sql("SELECT hour(t_start) h, COUNT(*) n FROM c WHERE t_start IS NOT NULL GROUP BY 1 ORDER BY 1").df()
fig, ax = plt.subplots(figsize=(7.4, 2.6))
hh = {int(r.h): r.n/1000 for r in h.itertuples()}
ax.bar(range(24), [hh.get(i, 0) for i in range(24)], color=ORANGE, width=0.62)
ax.set_xticks(range(0, 24, 2))
ax.set_title("Collection start times: two shifts (60,916 timestamped rows)")
ax.set_ylabel("rows (thousands)")
ax.set_xlabel("start hour")
ax.annotate("early shift 04\u201306 h", xy=(5, 8.4), fontsize=8.5, color=INK2, ha="center")
ax.annotate("afternoon shift 14\u201315 h", xy=(14.5, 22), fontsize=8.5, color=INK2, ha="center")
style(ax); ax.grid(axis="y")
save(fig, "F5_shift_structure")

# ---- F6: sensor negatives by year ----
ny = pd.DataFrame(V["effective_windows"]["sensor_neg_share_by_year"])
fig, ax = plt.subplots(figsize=(7.4, 2.5))
ax.bar(ny.y.astype(str), ny.neg_pct, color=BLUE, width=0.5)
for i, r in ny.iterrows():
    ax.text(i, r.neg_pct+0.8, f"{r.neg_pct}%", ha="center", fontsize=8.5, color=INK2)
ax.bar(["2024"], [ny[ny.y == 2024].neg_pct.iloc[0]], color=GRID, width=0.5)
ax.text(4, ny[ny.y == 2024].neg_pct.iloc[0]+0.8, "2.6%\n(partial yr)", ha="center", fontsize=7.5, color=MUTED)
ax.set_title("Share of negative sensor readings by year")
ax.set_ylabel("% of readings")
style(ax); ax.grid(axis="y")
save(fig, "F6_negatives_by_year")
print("ALL_FIGURES_DONE")
