# tablesim: when should a booking pick its table?

Elyra's site lists voice booking, email handling and "Table Allocation" ("Every seat filled with the right guest. Walk-ins seated in seconds.") (https://www.elyrasystems.com/), and its launch post says new venues see "record occupancy within weeks". A reservation system makes two decisions that look like one: which bookings to accept, and which table each party gets. If the table is fixed at booking time, a party that overstays delays whoever was promised that table. This is a one-evening restaurant simulator that measures the difference.

## The setup
`tablesim/sim.py`: 8 two-tops, 6 four-tops and 2 six-tops, with adjacent tables combinable (2+2, 4+2, 4+4). Requests arrive with a size (mostly 2 and 4) and a preferred time (peaks around 19:00 and 21:00); a request takes the nearest free 15-minute slot within 30 minutes. A booking holds its unit for the party's mean dwell (60 + 9 min per guest) plus a buffer. In service, dwell times are random (log-normal), a share of bookings are no-shows, and arrivals are a few minutes early or late. Policies:
- **first fit / best fit** at booking (best fit = smallest unit that seats the party),
- table **fixed at booking** vs **chosen at arrival** (the unit that lets the party sit soonest, then the tightest fit),
- buffer 0 / 10 / 20 minutes.

## Results (40 simulated evenings each)
Dev: ~60 requests an evening, dwell spread 0.30, 8% no-shows. Held-out (seeds 1000-1039, fixed in git before the first run): ~85 requests, 4 points more large parties, dwell spread 0.45, 12% no-shows.

| Held-out | covers seated | booked parties | mean wait | share waiting > 15 min |
|---|---|---|---|---|
| first fit, table fixed, buffer 10 | 102.5 | 39.0 | 5.6 min | 10.2% |
| best fit, table fixed, buffer 10 | 102.3 | 38.9 | 5.3 | 9.4% |
| best fit, table chosen at arrival, buffer 10 | 102.3 | 38.9 | 0.4 | 0.8% |
| best fit, table chosen at arrival, **buffer 0** | **110.5** | 40.9 | 0.4 | 1.1% |
| best fit, table chosen at arrival, buffer 20 | 95.2 | 36.0 | 0.2 | 0.6% |

- Choosing the table at arrival removes almost all the waiting (5.3 to 0.4 min) at no cost in covers.
- That makes room for a tighter buffer: buffer 0 seats 8% more covers than buffer 10 with the same waiting. A 20-minute buffer gives up 7% of covers for no visible benefit.
- First fit vs best fit made almost no difference here.
- Dev shows the same pattern (waits 2.3 to 0.2 min; buffer 0 gives +6% covers).

## Read this before believing the table
My restaurant: one seating shape, independent parties, no walk-ins, no server sections, no kitchen pacing, no deposits, and "choose at arrival" assumes the host can seat any party at any free table. Real restaurants refuse that last assumption for good reasons. About 40% of requests are declined here, a capacity limit of my invented floor. Nothing here uses Elyra data or systems.

## Run it (3 commands)
```
pip install pytest
python -m pytest -q tests
python -m tablesim.run
```
Standard library only. 4 tests.

Unofficial prototype by Kushagra Pratap Singh. Not affiliated with Elyra.
