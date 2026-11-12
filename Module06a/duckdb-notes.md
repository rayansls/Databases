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
- Dashboard ratio: ~100x faster in DuckDB.
- Monthly ratio: ~40x faster in DuckDB.
- Why the difference? The `strftime()` function in the monthly query does per-row work, which dominates DuckDB's fast scan. SQLite's slow scan hides it.

## Round 4 — plan observations
- Evidence file: `plan-results.txt`
- The DuckDB plan explicitly shows it only read 4 columns (`machine_id, site, technician, part_price`) instead of all 7.
- It scanned 2,000,000 rows, but grouped them down to 350. 
- SQLite uses a `SCAN` over full rows and a `TEMP B-TREE FOR GROUP BY`.

## Round 5 — boundary numbers
<fill in after Round 5>