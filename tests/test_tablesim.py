from tablesim import sim


def test_bookings_never_overlap_on_a_table():
    for s in range(5):
        b = sim.book(sim.make_requests(s, 70), "best", 10)
        for t in range(len(sim.TABLES)):
            iv = sorted((x["start"], x["start"] + sim.mean_dwell(x["size"]) + 10) for x in b if t in x["unit"])
            assert all(a[1] <= c[0] for a, c in zip(iv, iv[1:]))


def test_party_fits_its_unit():
    b = sim.book(sim.make_requests(2, 70), "first", 10)
    assert b and all(sim.CAP(x["unit"]) >= x["size"] for x in b)


def test_service_is_deterministic_and_waits_nonnegative():
    b = sim.book(sim.make_requests(3, 60), "best", 10)
    a, c = sim.serve(b, "flex", 3), sim.serve(b, "flex", 3)
    assert a == c and a["mean_wait"] >= 0


def test_flexible_seating_waits_no_more_than_fixed_on_average():
    f = [sim.serve(sim.book(sim.make_requests(s, 80), "best", 10), "fixed", s)["mean_wait"] for s in range(10)]
    x = [sim.serve(sim.book(sim.make_requests(s, 80), "best", 10), "flex", s)["mean_wait"] for s in range(10)]
    assert sum(x) <= sum(f)
