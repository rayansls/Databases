# Module 6a — DuckDB notes

## Round 2 — honesty check (passed)
- history.db rows: 2000000
- parquet rows: 2000000
- SUM(part_price) SQLite: 21000000.0
- SUM(part_price) Parquet: 21000000.0
- MATCH
- parquet size: 2.4 MB

## Round 3 — race
- Evidence file: `race-results.txt`
- Dashboard: SQLite 280.7 ms vs DuckDB 21.8 ms (median of 5) → 12.9x faster in DuckDB.
- Monthly: SQLite 2287.2 ms vs DuckDB 51.8 ms (median of 5) → 44.2x faster in DuckDB.
- My ratios are the other way round from the example in the module (~100x dashboard, ~30-60x monthly). Why the monthly ratio is higher on my laptop: the dashboard has a `WHERE done_on = ...`, so SQLite throws most rows away early and only groups a few. The monthly report has to compute the month and group every one of the 2,000,000 rows, one row at a time in SQLite, which is exactly the kind of work DuckDB does on whole columns at once.

## Round 4 — plan observations
- Evidence file: `plan-results.txt`
- The DuckDB plan explicitly shows it only read 4 columns (`machine_id, site, technician, part_price`) instead of all 7.
- It scanned 2,000,000 rows, but grouped them down to 350. 
- SQLite uses a `SCAN` over full rows and a `TEMP B-TREE FOR GROUP BY`.

## Round 5 — boundary numbers
- Evidence file: `boundary-results.txt` (script: `boundary_batched.py`)
- 1,000 inserts of one row each: SQLite 1.8 ms, DuckDB 3947.0 ms (all rows given to one `executemany` call).
- DuckDB is the wrong engine for many small writes: that is OLTP work, not OLAP.