"""One restaurant evening: bookings accepted by a rule, then service with real (random) dwell times.

Tables: 8 two-tops, 6 four-tops, 2 six-tops; two tables can be combined (2+2 -> 4, 4+2 -> 6, 4+4 -> 8).
A booking holds its table(s) for mean dwell + buffer. In service, dwell times vary, so a table may free late.
Policies = how a booking picks its table (first fit / best fit), whether the table is fixed at booking time or chosen
at arrival from whatever is free ("flexible"), and the buffer.
"""
import itertools
import math
import random

TABLES = [2] * 8 + [4] * 6 + [6] * 2
UNITS = [(i,) for i in range(len(TABLES))]
UNITS += [(i, j) for i, j in itertools.combinations(range(len(TABLES)), 2) if (TABLES[i], TABLES[j]) in ((2, 2), (4, 2), (2, 4), (4, 4)) and abs(i - j) <= 2]
CAP = lambda u: sum(TABLES[i] for i in u) if len(u) == 1 else (4 if sum(TABLES[i] for i in u) == 4 else sum(TABLES[i] for i in u) - 0)
SIZES = [1, 2, 3, 4, 5, 6, 8]


def mean_dwell(size):
    return 60 + 9 * size


def make_requests(seed, lam, big_share=0.0):
    rng = random.Random(seed)
    w = [0.03, 0.50, 0.10, 0.22, 0.06, 0.06 + big_share, 0.03 + big_share]
    reqs = []
    for rid in range(int(rng.gauss(lam, 4))):
        size = rng.choices(SIZES, w)[0]
        pref = int(min(330, max(0, rng.choice([rng.gauss(120, 40), rng.gauss(240, 45)]))) // 15 * 15)
        reqs.append({"id": rid, "size": size, "pref": pref})
    return reqs


def book(reqs, assign, buffer):
    """Accept in arrival order: nearest feasible 15-minute slot within +-30 min; hold units by mean dwell + buffer."""
    busy = {i: [] for i in range(len(TABLES))}
    out = []
    for r in reqs:
        dur = mean_dwell(r["size"]) + buffer
        best = None
        for off in (0, -15, 15, -30, 30):
            s = r["pref"] + off
            if s < 0 or s > 330:
                continue
            cands = [u for u in UNITS if CAP(u) >= r["size"] and all(all(s + dur <= a or s >= b for a, b in busy[i]) for i in u)]
            if cands:
                if assign == "first":
                    u = cands[0]
                else:
                    u = min(cands, key=lambda u: (CAP(u) - r["size"], len(u)))
                best = (s, u)
                break
        if best:
            s, u = best
            for i in u:
                busy[i].append((s, s + dur))
            out.append(dict(r, start=s, unit=u))
    return out


def serve(bookings, service, seed, sigma=0.30, no_show=0.08):
    rng = random.Random(seed * 31 + 7)
    free = [0.0] * len(TABLES)
    waits, covers = [], 0
    arrivals = []
    for b in bookings:
        if rng.random() < no_show:
            continue
        arrivals.append((b["start"] + rng.uniform(-5, 10), b))
    arrivals.sort(key=lambda x: x[0])
    for arr, b in arrivals:
        dwell = mean_dwell(b["size"]) * math.exp(rng.gauss(-sigma ** 2 / 2, sigma))
        if service == "fixed":
            unit = b["unit"]
        else:   # flexible: the unit that lets this party sit soonest, then the tightest fit
            unit = min((u for u in UNITS if CAP(u) >= b["size"]), key=lambda u: (max(arr, max(free[i] for i in u)), CAP(u) - b["size"]))
        seat = max(arr, max(free[i] for i in unit))
        for i in unit:
            free[i] = seat + dwell
        waits.append(seat - arr)
        covers += b["size"]
    waits.sort()
    return {"covers": covers, "mean_wait": sum(waits) / max(1, len(waits)), "p90_wait": waits[int(0.9 * (len(waits) - 1))] if waits else 0.0,
            "late15": sum(1 for w in waits if w > 15) / max(1, len(waits)), "booked": len(bookings)}
