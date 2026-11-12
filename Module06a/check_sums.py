# Module06a/check_sums.py — verify Parquet and SQLite agree before timing anything.
import sqlite3
from pathlib import Path

import duckdb

here = Path(__file__).parent
db = here / "history.db"
parquet = here / "report_history.parquet"

sq_rows, sq_sum = sqlite3.connect(db).execute(
    "SELECT COUNT(*), ROUND(SUM(part_price), 2) FROM report_history"
).fetchone()

pq_rows, pq_sum = duckdb.connect().execute(
    f"SELECT COUNT(*), ROUND(SUM(part_price), 2) FROM read_parquet('{parquet}')"
).fetchone()

print(f"sqlite  rows={sq_rows:>10}  sum={sq_sum}")
print(f"parquet rows={pq_rows:>10}  sum={pq_sum}")
print("MATCH" if (sq_rows, sq_sum) == (pq_rows, pq_sum) else "MISMATCH")

# also check the csv, for completeness
csv_rows = sqlite3.connect(db).execute(
    "SELECT COUNT(*) FROM report_history"
).fetchone()  # placeholder; csv is the 200k base set, so we check separately
print(f"csv is the 200k base set — not compared here")