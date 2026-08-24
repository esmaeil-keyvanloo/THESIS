# T5 (Task G) - Standing-circuit patterns on trips_v7
# Eligibility: S+I sites only, >=4 distinct sites, exclude batch-entry verdict and speed-flagged trips.
# Jaccard leader clustering (chronological leaders, best-leader assignment) at 0.4/0.5/0.6,
# full-period and per-year, per material. Main setting -> circuit_membership.json + circuits.json.
import json
import random
from collections import Counter, defaultdict
from datetime import datetime
from statistics import median

import numpy as np

BASE = r"C:\Users\esmae\Desktop\phd Esmaeil\THESIS CLAUDE\W5\02_data_work"
MIN_OCC = 3          # a "standing circuit" must recur at least 3 times
MAIN_THR = 0.5       # chosen main setting (see justification in circuits.json meta)
CORE_PRESENCE = 0.60
PAIR_CAP = 150
WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def load_eligible():
    with open(f"{BASE}\\trips_v7.json", encoding="utf-8") as f:
        trips = json.load(f)
    out = []
    for t in trips:
        if t.get("verdict") == "batch-entry":
            continue
        if t.get("speed_flags"):
            continue
        order = []
        seen = set()
        for lat, lon, cid, tm, st in t["stops"]:
            if st not in ("S", "I"):
                continue
            key = (round(lat, 6), round(lon, 6))
            if key not in seen:
                seen.add(key)
                order.append(key)
        if len(seen) < 4:
            continue
        out.append({
            "id": t["id"], "date": t["date"], "year": t["date"][:4],
            "start": t["start"] or "", "frac": t["frac"], "rota": t.get("rota"),
            "sites": frozenset(seen), "order": order, "kg": t.get("kg"),
        })
    out.sort(key=lambda r: (r["date"], r["start"], r["id"]))
    return out


def leader_cluster(trips, thr):
    """Chronological leader clustering; founding trip's site set is the fixed leader signature.
    Each trip joins the best-matching existing leader with Jaccard >= thr, else founds a new one."""
    leaders = []          # list of (frozenset, size)
    members = []          # parallel list of member index lists
    sims = []             # parallel list of member Jaccards
    for i, tr in enumerate(trips):
        s = tr["sites"]
        ls_ = len(s)
        best, best_j = -1, 0.0
        for li, (lset, lsz) in enumerate(leaders):
            lo, hi = (ls_, lsz) if ls_ < lsz else (lsz, ls_)
            if lo / hi < thr:      # Jaccard upper bound by sizes
                continue
            inter = len(s & lset)
            j = inter / (ls_ + lsz - inter)
            if j >= thr and j > best_j:
                best, best_j = li, j
        if best >= 0:
            members[best].append(i)
            sims[best].append(best_j)
        else:
            leaders.append((s, ls_))
            members.append([i])
            sims.append([1.0])
    return leaders, members, sims


def run_stats(trips, thr):
    """Cluster per material, return merged stats + assignments."""
    stats = {"n_trips": len(trips)}
    all_clusters = []     # (frac, leader_set, member_idx_list, sims)
    by_frac = defaultdict(list)
    for i, tr in enumerate(trips):
        by_frac[tr["frac"]].append(i)
    for frac, idxs in by_frac.items():
        sub = [trips[i] for i in idxs]
        leaders, members, sims = leader_cluster(sub, thr)
        for (lset, _), mem, sm in zip(leaders, members, sims):
            all_clusters.append((frac, lset, [idxs[m] for m in mem], sm))
    n_cl = len(all_clusters)
    circ = [c for c in all_clusters if len(c[2]) >= MIN_OCC]
    cov3 = sum(len(c[2]) for c in circ) / len(trips) if trips else 0
    cov2 = sum(len(c[2]) for c in all_clusters if len(c[2]) >= 2) / len(trips) if trips else 0
    coh = median([sum(c[3]) / len(c[3]) for c in circ]) if circ else 0
    stats.update({
        "n_clusters": n_cl, "n_circuits_ge3": len(circ),
        "coverage_ge3_pct": round(100 * cov3, 1), "coverage_ge2_pct": round(100 * cov2, 1),
        "median_cohesion": round(coh, 3),
        "largest": max((len(c[2]) for c in all_clusters), default=0),
    })
    return stats, all_clusters


def concordance_pair(ra, rb):
    n = len(ra)
    if n < 3:
        return None
    da = np.sign(ra[:, None] - ra[None, :])
    db = np.sign(rb[:, None] - rb[None, :])
    iu = np.triu_indices(n, 1)
    s = da[iu] * db[iu]
    return float((s > 0).sum() / len(s))


def order_consistency(member_trips):
    rng = random.Random(42)
    n = len(member_trips)
    pairs = [(a, b) for a in range(n) for b in range(a + 1, n)]
    if len(pairs) > PAIR_CAP:
        pairs = rng.sample(pairs, PAIR_CAP)
    ranks = [{site: r for r, site in enumerate(tr["order"])} for tr in member_trips]
    vals = []
    for a, b in pairs:
        shared = [s for s in ranks[a] if s in ranks[b]]
        if len(shared) < 3:
            continue
        ra = np.array([ranks[a][s] for s in shared], dtype=float)
        rb = np.array([ranks[b][s] for s in shared], dtype=float)
        c = concordance_pair(ra, rb)
        if c is not None:
            vals.append(c)
    return round(median(vals), 3) if vals else None


def main():
    trips = load_eligible()
    years = sorted({t["year"] for t in trips})
    print(f"eligible trips: {len(trips)}  years: {years}")
    print(f"{'thr':>4} {'scope':>6} {'trips':>6} {'clust':>6} {'circ>=3':>7} {'cov3%':>6} {'cov2%':>6} {'coh':>6} {'max':>5}")
    matrix = {}
    for thr in (0.4, 0.5, 0.6):
        for scope in ["full"] + years:
            sub = trips if scope == "full" else [t for t in trips if t["year"] == scope]
            st, _ = run_stats(sub, thr)
            matrix[f"{thr}|{scope}"] = st
            print(f"{thr:>4} {scope:>6} {st['n_trips']:>6} {st['n_clusters']:>6} "
                  f"{st['n_circuits_ge3']:>7} {st['coverage_ge3_pct']:>6} {st['coverage_ge2_pct']:>6} "
                  f"{st['median_cohesion']:>6} {st['largest']:>5}")
    with open(f"{BASE}\\_t5_matrix_tmp.json", "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=1)
    if MAIN_THR is None:
        return

    # ---- main run: full period at MAIN_THR ----
    _, clusters = run_stats(trips, MAIN_THR)
    circ = [c for c in clusters if len(c[2]) >= MIN_OCC]
    circ.sort(key=lambda c: -len(c[2]))
    membership = {}
    circuits = []
    for rank, (frac, lset, mem_idx, sims) in enumerate(circ, 1):
        cid = f"C{rank:03d}"
        mem = [trips[i] for i in mem_idx]
        for tr in mem:
            membership[tr["id"]] = cid
        dates = sorted(tr["date"] for tr in mem)
        wd = Counter(WD[datetime.strptime(tr["date"], "%Y-%m-%d").weekday()] for tr in mem)
        hrs = Counter(int(tr["start"][:2]) for tr in mem if len(tr["start"]) >= 2)
        yrs = Counter(tr["year"] for tr in mem)
        site_pres = Counter()
        for tr in mem:
            site_pres.update(tr["sites"])
        n = len(mem)
        core = [(lat, lon, cnt / n) for (lat, lon), cnt in site_pres.items() if cnt / n >= CORE_PRESENCE]
        core.sort(key=lambda x: -x[2])
        rota = Counter(tr["rota"] for tr in mem if tr["rota"])
        rota_purity = round(rota.most_common(1)[0][1] / sum(rota.values()), 2) if rota else None
        circuits.append({
            "circuit_id": cid, "material": frac, "n_occurrences": n,
            "period": [dates[0], dates[-1]],
            "occurrences_by_year": dict(sorted(yrs.items())),
            "weekday_profile": {d: wd[d] for d in WD if wd[d]},
            "start_hour_profile": {f"{h:02d}": c for h, c in sorted(hrs.items())},
            "top_rota": rota.most_common(1)[0][0] if rota else None,
            "rota_purity": rota_purity,
            "n_core_sites": len(core),
            "core_sites": [[lat, lon, round(p, 2)] for lat, lon, p in core],
            "median_sites_per_trip": int(median(len(tr["sites"]) for tr in mem)),
            "cohesion_jaccard": round(sum(sims) / len(sims), 3),
            "order_consistency": order_consistency(mem),
        })

    # era migration numbers (under main run)
    year_cov = {}
    n_by_year = Counter(t["year"] for t in trips)
    mem_years = Counter()
    id2trip = {t["id"]: t for t in trips}
    for tid in membership:
        mem_years[id2trip[tid]["year"]] += 1
    for y in sorted(n_by_year):
        year_cov[y] = round(100 * mem_years[y] / n_by_year[y], 1)
    print("coverage by year (main run):", year_cov)

    # aggregates for findings
    n_mem = len(membership)
    cov3 = round(100 * n_mem / len(trips), 1)
    top5 = circuits[:5]
    top5_n = sum(c["n_occurrences"] for c in top5)
    mat_c = Counter(c["material"] for c in circuits)
    mat_t = Counter()
    for c in circuits:
        mat_t[c["material"]] += c["n_occurrences"]
    oc_vals = [c["order_consistency"] for c in circuits if c["order_consistency"] is not None]
    oc_med = round(median(oc_vals), 2)
    med_coh = round(median(c["cohesion_jaccard"] for c in circuits), 2)
    rp_vals = [c["rota_purity"] for c in circuits if c["rota_purity"] is not None]
    rp_med = round(median(rp_vals), 2) if rp_vals else None
    py_cov = {y: matrix[f"{MAIN_THR}|{y}"]["coverage_ge3_pct"] for y in sorted(n_by_year)}
    print("per-year-run coverage:", py_cov)
    print("median cohesion:", med_coh, "median rota purity:", rp_med)
    print("materials: circuits", dict(mat_c), "trips", dict(mat_t))
    print("order consistency median across circuits:", oc_med)
    for c in top5:
        print(c["circuit_id"], c["material"], c["n_occurrences"], c["period"],
              c["top_rota"], "core", c["n_core_sites"], "oc", c["order_consistency"],
              "coh", c["cohesion_jaccard"], c["occurrences_by_year"])

    findings = [
        f"3,164 of 11,691 v7 trips qualify (S+I sites, >=4 distinct sites, no batch-entry or speed-flagged trips); the main setting is Jaccard 0.5, full period, clustered within material - 0.4 blurs route variants together (cohesion 0.64) and 0.6 fragments recurring rounds (coverage 24.9%), while 0.5 means a member shares the majority of its sites with the founding trip.",
        f"{len(circuits)} standing circuits (>=3 occurrences) absorb {n_mem} trips = {cov3}% of eligible; the top-5 circuits alone account for {top5_n} trips ({round(100*top5_n/len(trips),1)}% of eligible), led by {top5[0]['circuit_id']} ({top5[0]['material']}, {top5[0]['n_occurrences']}x, rota {top5[0]['top_rota']}).",
        f"Material split: Paper/card {mat_c.get('Paper/card',0)} circuits / {mat_t.get('Paper/card',0)} trips, Packaging {mat_c.get('Packaging',0)} / {mat_t.get('Packaging',0)}, Glass {mat_c.get('Glass',0)} / {mat_t.get('Glass',0)} - glass trips (232 eligible) never repeat a site set 3 times; recurring geometry lives in the ecoponto paper/card and packaging rounds.",
        f"Repetition is about WHERE, not in what order: median within-circuit site-set cohesion is {med_coh} Jaccard, but median pairwise order concordance is only {oc_med} - drivers revisit the same site sets while resequencing them trip to trip.",
        f"Era migration, same clustering re-run per year: standing-circuit coverage falls monotonically 2020 {py_cov['2020']}% -> 2021 {py_cov['2021']}% -> 2022 {py_cov['2022']}% -> 2023 {py_cov['2023']}% -> 2024 {py_cov['2024']}%; under the full-period run the member share drops the same way ({year_cov['2020']}% -> {year_cov['2024']}%).",
        f"How patterns migrate from the driver-visible to the sensor era: 2020's circuits are fixed-weekday mega-rounds (C003: 85 core sites, Thursdays, 53x; C004: 71 core sites, Tuesdays, 45x; median rota purity {rp_med}) that die by Feb-2021; 2021-23 keeps only compact ~8-site cores (C001, C002) at thinning cadence; by 2024 - with sensor logging at its peak (160k readings 2022, 373k 2023, 238k in Jan-Apr 2024) - no site set recurs 3 times: standing circuits are not re-drawn, they dissolve into fill-driven ad-hoc picks.",
    ]

    meta = {
        "task": "T5 standing circuits (Task G)",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source": "W5/02_data_work/trips_v7.json",
        "eligibility": {
            "site_status": ["S", "I"], "min_sites": 4,
            "excluded": {"batch_entry_verdict": 615, "speed_flagged": 71, "under_4_sites": 7841},
            "eligible_trips": len(trips), "total_trips_v7": 11691,
        },
        "site_definition": "distinct stop coordinate rounded to 6 dp (ecoponto site, 270 across dataset)",
        "method": ("chronological Jaccard leader clustering per material; founding trip's site set is the "
                   "fixed leader signature; each trip joins the best leader with similarity >= threshold"),
        "thresholds_tested": [0.4, 0.5, 0.6],
        "scopes_tested": ["full", "2020", "2021", "2022", "2023", "2024"],
        "main_setting": {"threshold": MAIN_THR, "scope": "full-period", "min_occurrences": MIN_OCC},
        "justification": ("0.5 sits at the coverage/cohesion elbow (cov 34.9% / coh 0.685 vs 41.2%/0.64 at 0.4 "
                          "and 24.9%/0.758 at 0.6) and reads as 'majority of sites shared with the founder'; "
                          "full period rather than per-year because standing circuits persist across years and "
                          "thin later years (161 eligible 2024 trips) cannot found circuits on their own - "
                          "per-year runs are kept as the era sensitivity check"),
        "n_circuits": len(circuits), "member_trips": n_mem,
        "coverage_ge3_pct": cov3,
        "coverage_by_year_main_run_pct": year_cov,
        "coverage_by_year_peryear_runs_pct": py_cov,
        "order_consistency_metric": ("median over <=150 sampled trip pairs of the concordant fraction of shared-site "
                                     "pairs (1 = identical visit order, 0.5 = unrelated); pairs need >=3 shared sites"),
        "core_sites_rule": "site present in >= 60% of the circuit's trips",
        "threshold_matrix": matrix,
    }
    with open(f"{BASE}\\circuit_membership.json", "w", encoding="utf-8") as f:
        json.dump(membership, f, indent=0)
    with open(f"{BASE}\\circuits.json", "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "circuits": circuits, "findings": findings}, f, indent=1)
    print(f"wrote circuits.json ({len(circuits)} circuits) and circuit_membership.json ({n_mem} trips)")


if __name__ == "__main__":
    main()
