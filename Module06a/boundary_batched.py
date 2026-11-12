import sqlite3
import time
import duckdb

print("Starting boundary test...") # Added this to prove it runs

N = 1_000

con1 = sqlite3.connect(":memory:")
con1.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT, v REAL)")

t0 = time.perf_counter()
for i in range(N):
    con1.execute("INSERT INTO s VALUES (?, ?, ?)", (i, f"k{i}", i * 1.5))
con1.commit()
sqlite_insert = (time.perf_counter() - t0) * 1000
print(f"SQLite inserts: {sqlite_insert:.1f} ms")

con2 = duckdb.connect()
con2.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT, v DOUBLE)")

rows = [(i, f"k{i}", i * 1.5) for i in range(N)]
t0 = time.perf_counter()
con2.executemany("INSERT INTO s VALUES (?, ?, ?)", rows)
duck_insert = (time.perf_counter() - t0) * 1000
print(f"DuckDB batched inserts: {duck_insert:.1f} ms")