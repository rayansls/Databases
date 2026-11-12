# Module06a/plan_sqlite.py
import sqlite3
from pathlib import Path

here = Path(__file__).parent
db = here / "history.db"

sql = """
EXPLAIN QUERY PLAN
SELECT machine_id, site, technician, SUM(part_price) AS cost
FROM report_history WHERE done_on >= '2026-01-01'
GROUP BY machine_id, site, technician
"""

con = sqlite3.connect(db)
for row in con.execute(sql):
    print(row)