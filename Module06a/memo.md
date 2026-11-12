# Memo — Analytical copy of the month-end report

**To:** Lea Winter, Yasmin Kaya
**From:** [Your Name]
**Date:** November 12, 2026
**Re:** Moving the month-end report off the operational database

The month-end report moves to a Parquet file (`report_history.parquet`, 2.4 MB) produced from `history.db` by `to_parquet.py`; the operational `report_history` table stays in SQLite as the system of record.

On 2,000,000 rows, the dashboard aggregate runs in a median of <PASTE SQLITE DASHBOARD TIME HERE> ms in SQLite versus <PASTE DUCKDB DASHBOARD TIME HERE> ms in DuckDB (a <PASTE RATIO HERE>× speedup). The `SUM(part_price)` check returns 21000000.0 on both sides, proving the data matches perfectly.

The Parquet is refreshed by a nightly `to_parquet.py` run after the shift. If the refresh silently stops, the dashboard reports stale numbers within one day — detectable by comparing the max `done_on` in the Parquet against the SQLite max, and by running `check_sums.py` on a schedule.

We would not move the point-lookup and per-row write workload: 1,000 single-row inserts take 1.8 ms in SQLite versus 3947.0 ms in DuckDB. Batching helps DuckDB but does not close the gap; that workload is OLTP, not OLAP. 

Recommendation: adopt the Parquet copy for the month-end report; keep SQLite for operational writes and point lookups; wire the refresh to the nightly job with a check gate.