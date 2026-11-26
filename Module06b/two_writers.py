# Module06b/two_writers.py — run with:  uv run python Module06b/two_writers.py
"""The SQLite fallback for Task 1: two writers, one row, one file.

Writer A opens a write transaction (BEGIN IMMEDIATE) and does not commit yet.
Writer B tries to write the same row at the same time.
"""
import sqlite3
from pathlib import Path

here = Path(__file__).parent
path = here / "boundary.db"

setup = sqlite3.connect(path)
setup.executescript("""
DROP TABLE IF EXISTS machine;
CREATE TABLE machine(
    machine_id      INTEGER PRIMARY KEY,
    site            TEXT NOT NULL,
    parts_produced  INTEGER NOT NULL DEFAULT 0
);
INSERT INTO machine VALUES (1, 'guetersloh', 0);
""")
setup.close()

# isolation_level=None: we write BEGIN and COMMIT ourselves; timeout=0: do not wait
a = sqlite3.connect(path, isolation_level=None, timeout=0)
b = sqlite3.connect(path, isolation_level=None, timeout=0)

a.execute("BEGIN IMMEDIATE")
a.execute("UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1")
print("writer A: updated the row, transaction still open")

try:
    b.execute("BEGIN IMMEDIATE")
    b.execute("UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1")
    print("writer B: updated the row (unexpected)")
except sqlite3.OperationalError as e:
    print("writer B:", e)

a.execute("COMMIT")
print("writer A: committed")

b.execute("BEGIN IMMEDIATE")
b.execute("UPDATE machine SET parts_produced = parts_produced + 1 WHERE machine_id = 1")
b.execute("COMMIT")
print("writer B: retried after A committed, and succeeded")

print("parts_produced is now:",
      b.execute("SELECT parts_produced FROM machine WHERE machine_id = 1").fetchone()[0])
a.close()
b.close()
