import json
from statistics import mean

from . import sim

POLICIES = {"first fit, table fixed at booking, buffer 10": ("first", "fixed", 10),
            "best fit, table fixed at booking, buffer 10": ("best", "fixed", 10),
            "best fit, table chosen at arrival, buffer 10": ("best", "flex", 10),
            "best fit, table chosen at arrival, buffer 0": ("best", "flex", 0),
            "best fit, table chosen at arrival, buffer 20": ("best", "flex", 20)}
SPLITS = {"dev": (range(0, 40), dict(lam=60, big_share=0.0), dict(sigma=0.30, no_show=0.08)),
          "held_out": (range(1000, 1040), dict(lam=85, big_share=0.04), dict(sigma=0.45, no_show=0.12))}


def evaluate(seeds, rq, sv):
    out = {}
    for name, (assign, service, buf) in POLICIES.items():
        rs = []
        for s in seeds:
            b = sim.book(sim.make_requests(s, **rq), assign, buf)
            rs.append(sim.serve(b, service, s, **sv))
        out[name] = {k: round(mean(r[k] for r in rs), 3 if k == "late15" else 1) for k in rs[0]}
    return out


def main():
    res = {k: evaluate(*v) for k, v in SPLITS.items()}
    json.dump(res, open("out/result.json", "w"), indent=1)
    for k, v in res.items():
        print(k)
        for n, d in v.items():
            print(f"  {n:46}", d)


if __name__ == "__main__":
    main()
