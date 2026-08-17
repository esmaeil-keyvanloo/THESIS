"""W2 - Event-level comparison figures F7-F9 (same style as build_figures.py)."""
import duckdb, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
OUT = f"{BASE}/W2/03_outputs/figures"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
CRIT = "#d03b3b"
SURF, INK, INK2, MUTED, GRID, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 9,
    "figure.facecolor": SURF, "axes.facecolor": SURF,
    "axes.edgecolor": BASELINE, "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "text.color": INK, "axes.labelcolor": INK2,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False,
})
R = json.load(open(f"{BASE}/W2/02_data_work/match_stats.json", encoding="utf-8"))

def style(ax):
    ax.grid(axis="x", visible=False); ax.grid(axis="y"); ax.tick_params(length=0)

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=200, bbox_inches="tight", facecolor=SURF)
    plt.close(fig); print("wrote", name)

# F7: window sensitivity, two panels (one measure per axis)
ws = pd.DataFrame(R["window_sensitivity"])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.8))
x = range(len(ws))
labels = [f"{w}m" if w < 60 else f"{w//60}h" for w in ws.window_min]
a1.bar(x, ws.pct_of_driver_rows, color=[BLUE if w == 180 else "#9ec5f4" for w in ws.window_min], width=0.55)
a1.set_xticks(list(x), labels)
a1.set_title("Driver rows matched to a sensor reading (%)")
for i, v in enumerate(ws.pct_of_driver_rows):
    a1.text(i, v + 1.5, f"{v:.0f}", ha="center", fontsize=8, color=INK2)
a1.text(3, 78, "chosen: ±3 h", fontsize=8, color=BLUE, ha="center", fontweight="bold")
a1.set_ylim(0, 85)
a2.bar(x, ws.acceptable_pct_of_matched, color=[AQUA if w == 180 else "#9fdcc4" for w in ws.window_min], width=0.55)
a2.set_xticks(list(x), labels)
a2.set_ylim(0, 60)
a2.axhline(50, color=MUTED, lw=0.8, ls="--")
a2.set_title("Acceptable agreement among matched (%)")
for i, v in enumerate(ws.acceptable_pct_of_matched):
    a2.text(i, v + 1.5, f"{v:.0f}", ha="center", fontsize=8, color=INK2)
for a in (a1, a2): style(a)
save(fig, "F7_window_sensitivity")

# F8: agreement categories + by driver value
dc = R["diff_categories"]; bd = pd.DataFrame(R["diff_by_driver_value"])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.8), width_ratios=[2, 3])
cats = [("Small\n\u226412.5", dc["small_pct"], AQUA), ("Moderate\n12.5\u201325", dc["moderate_pct"], YELLOW), ("Large\n>25", dc["large_pct"], CRIT)]
a1.bar(range(3), [c[1] for c in cats], color=[c[2] for c in cats], width=0.5)
a1.set_xticks(range(3), [c[0] for c in cats], fontsize=8)
for i, c in enumerate(cats):
    a1.text(i, c[1] + 1.5, f"{c[1]}%", ha="center", fontsize=9, fontweight="bold")
a1.set_title(f"|driver \u2212 sensor| categories\n({dc['compared_pairs']:,} pairs, \u00b13 h)")
a1.set_ylim(0, 62)
a2.bar(range(len(bd)), bd.acceptable_pct, color=BLUE, width=0.5)
a2.set_xticks(range(len(bd)), [str(int(v)) for v in bd.d_fill])
a2.axhline(dc["acceptable_pct"], color=MUTED, lw=0.8, ls="--")
a2.text(4.4, dc["acceptable_pct"] + 1.5, f"overall {dc['acceptable_pct']}%", fontsize=8, color=MUTED, ha="right")
for i, v in enumerate(bd.acceptable_pct):
    a2.text(i, v + 1.5, f"{v:.0f}", ha="center", fontsize=8, color=INK2)
a2.set_title("Acceptable agreement by driver value (%)")
a2.set_xlabel("driver visual estimate")
a2.set_ylim(0, 85)
for a in (a1, a2): style(a)
save(fig, "F8_agreement")

# F9: negatives — monthly by cluster + episode lengths
con = duckdb.connect()
neg = con.sql(f"""
  SELECT strftime(TRY_CAST("Data da leitura" AS TIMESTAMP), '%Y-%m') ym,
    SUM(CASE WHEN TRY_CAST("Enchimento" AS INT) >= -9 THEN 1 ELSE 0 END) small_c,
    SUM(CASE WHEN TRY_CAST("Enchimento" AS INT) < -9 THEN 1 ELSE 0 END) large_c
  FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet'
  WHERE TRY_CAST("Enchimento" AS INT) < 0 GROUP BY 1 ORDER BY 1
""").df()
eps = con.sql(f"""
  SELECT len, COUNT(*) n FROM (
    SELECT cid, grp, COUNT(*) len FROM (
      SELECT trim(idcontentor) cid, TRY_CAST("Data da leitura" AS TIMESTAMP) ts,
             TRY_CAST("Enchimento" AS INT) fill,
        SUM(CASE WHEN TRY_CAST("Enchimento" AS INT) >= 0 THEN 1 ELSE 0 END)
          OVER (PARTITION BY trim(idcontentor) ORDER BY TRY_CAST("Data da leitura" AS TIMESTAMP)) grp
      FROM '{BASE}/Brain/03_db/parquet/raw_sensors.parquet') WHERE fill < 0
    GROUP BY cid, grp)
  GROUP BY len ORDER BY len
""").df()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.8), width_ratios=[3, 2])
xs = range(len(neg))
a1.bar(xs, neg.small_c, color=YELLOW, width=0.8, label="\u22121\u2026\u22129 (transient)")
a1.bar(xs, neg.large_c, bottom=neg.small_c, color=CRIT, width=0.8, label="\u221289\u2026\u2212116 (fault codes)")
ticks = [i for i, ym in enumerate(neg.ym) if ym.endswith("-01")]
a1.set_xticks(ticks, [neg.ym[i][:4] for i in ticks])
a1.set_title("Negative readings per month, by cluster")
a1.legend(fontsize=7.5, loc="upper right")
bins = [(1, "1"), (2, "2"), (3, "3-4"), (5, "5-9"), (10, "10-49"), (50, "\u226550")]
vals = []
for lo, lbl in bins:
    hi = {1: 2, 2: 3, 3: 5, 5: 10, 10: 50, 50: 10**9}[lo]
    vals.append(eps[(eps.len >= lo) & (eps.len < hi)].n.sum())
a2.bar(range(len(bins)), vals, color=ORANGE, width=0.55)
a2.set_xticks(range(len(bins)), [b[1] for b in bins], fontsize=8)
a2.set_title("Consecutive-negative episode length\n(29,885 episodes; max 1,226)")
a2.set_xlabel("readings per episode")
for a in (a1, a2): style(a)
save(fig, "F9_negatives_deepdive")
print("EVENT_FIGURES_DONE")
