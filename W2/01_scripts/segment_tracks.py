"""W2 - Split trip identifiers into physically consistent vehicle tracks.

Rule: a segment between consecutive stops is only allowed if the truck could
plausibly drive it: implied road speed = (straight-line km x 1.3 detour factor)
/ (time gap minus 2 min service), capped at VMAX. Stops that cannot follow the
current track open (or join) another track -> de-interleaves parallel vehicles
under one identifier and cuts impossible jumps.
Outputs: trips_v3.json + segmentation_stats.json
"""
import json, math
from collections import Counter

BASE = r"C:/Users/esmae/Desktop/phd Esmaeil/THESIS CLAUDE"
DETOUR = 1.3
SERVICE_MIN = 2.0

def hav_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))

def tmin(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

trips = json.load(open(f"{BASE}/W2/02_data_work/trips.json", encoding="utf-8"))

# ---- 1. implied-speed distribution over all consecutive pairs ----
speeds = []
for t in trips:
    if t["n_bins"] < 2:
        continue
    st = t["stops"]
    for a, b in zip(st[:-1], st[1:]):
        gap = tmin(b[3]) - tmin(a[3])
        if gap < 0:
            gap += 1440  # overnight wrap (rare)
        d = hav_km(a, b) * DETOUR
        v = d / max(gap - SERVICE_MIN, 0.5) * 60
        speeds.append(v)
speeds.sort()
def pct(p):
    return round(speeds[min(int(p / 100 * len(speeds)), len(speeds) - 1)], 1)
dist = {f"p{p}": pct(p) for p in (50, 75, 90, 95, 97, 99)}
share_over = {v: round(100 * sum(1 for s in speeds if s > v) / len(speeds), 2) for v in (40, 60, 80, 100, 150)}

VMAX = 60.0  # justified: collection truck between stops; see stats printed

# ---- 2. greedy track assignment inside each identifier ----
out = []
n_split = 0
parts_counter = Counter()
violations_before = sum(1 for s in speeds if s > VMAX)
for t in trips:
    if t["n_bins"] < 2:
        t2 = dict(t); t2["base_id"] = t["id"]; t2["part"] = ""; t2["n_parts"] = 1
        out.append(t2)
        continue
    tracks = []  # each: list of stops
    for s in t["stops"]:
        best, best_v = None, None
        for tr in tracks:
            last = tr[-1]
            gap = tmin(s[3]) - tmin(last[3])
            if gap < 0:
                gap += 1440
            v = hav_km(last, s) * DETOUR / max(gap - SERVICE_MIN, 0.5) * 60
            if v <= VMAX and (best_v is None or v < best_v):
                best, best_v = tr, v
        if best is None:
            tracks.append([s])
        else:
            best.append(s)
    parts_counter[len(tracks)] += 1
    if len(tracks) > 1:
        n_split += 1
    letters = "abcdefghijklmnopqrstuvwxyz"
    multi = [tr for tr in tracks if len(tr) >= 1]
    for i, tr in enumerate(multi):
        t2 = dict(t)
        t2["base_id"] = t["id"]
        t2["part"] = ("" if len(multi) == 1 else (letters[i] if i < 26 else f"z{i}"))
        t2["n_parts"] = len(multi)
        t2["id"] = f'{t["id"]}{t2["part"]}'
        t2["stops"] = tr
        t2["n_bins"] = len(tr)
        t2["start"], t2["end"] = tr[0][3], tr[-1][3]
        dh = (tmin(tr[-1][3]) - tmin(tr[0][3])) / 60
        t2["dur_h"] = round(dh + (24 if dh < 0 else 0), 2)
        t2["km_line"] = round(sum(hav_km(a, b) for a, b in zip(tr[:-1], tr[1:])), 1)
        out.append(t2)

# residual check
resid = 0
for t in out:
    st = t["stops"]
    for a, b in zip(st[:-1], st[1:]):
        gap = tmin(b[3]) - tmin(a[3])
        if gap < 0:
            gap += 1440
        if hav_km(a, b) * DETOUR / max(gap - SERVICE_MIN, 0.5) * 60 > VMAX:
            resid += 1

stats = {
    "segments_checked": len(speeds),
    "implied_speed_kmh": dist,
    "share_over_threshold_pct": share_over,
    "chosen_vmax_kmh": VMAX,
    "identifiers_multibin": sum(1 for t in trips if t["n_bins"] >= 2),
    "identifiers_split": n_split,
    "tracks_per_identifier": dict(sorted(parts_counter.items())),
    "violating_segments_before": violations_before,
    "violating_segments_after": resid,
    "tracks_multibin_after": sum(1 for t in out if t["n_bins"] >= 2),
}
json.dump(out, open(f"{BASE}/W2/02_data_work/trips_v3.json", "w", encoding="utf-8"), separators=(",", ":"))
json.dump(stats, open(f"{BASE}/W2/02_data_work/segmentation_stats.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(stats, indent=1))
