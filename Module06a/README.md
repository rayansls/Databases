# Module 6a  The Analytical Engine (DuckDB)

[← Module 5](../Module05/README.md) · [Back to my portfolio](../README.md) · [Reflection 6](../Reflections/ref06.md) · [Next: Module 6b →](../Module06b/README.md)

In Module 5 I built a reporting table to make the dashboard faster, but it was still inside SQLite, an engine designed to write and read *single rows* very quickly, like recording one maintenance job or looking up one part. A month-end report is a completely different kind of work: it reads millions of rows and squeezes them into a few totals. In this module I stretched the Module 5 report to ten quarters, 2,000,000 rows, moved it into a format built for analysis, and raced SQLite against DuckDB, an engine that stores data by column instead of by row. The goal was not to find "the best database" but to find out, with numbers, which engine fits which job. My notes are in [`duckdb-notes.md`](duckdb-notes.md).

## Learning goals

1. Move a table out of SQLite into **Parquet** reproducibly, from a script.
2. Run the **same aggregate** in SQLite and DuckDB and report the difference honestly (interleaved runs, median).
3. Read **`EXPLAIN ANALYZE`** and name the operator and row count that dominate.
4. State, with a number, **where DuckDB is the wrong engine**.
5. Recommend **what moves to the analytical copy** and how that copy stays fresh.

---

## 1. From SQLite to Parquet, with a script

Everything in this module is rebuilt by scripts, so anyone can repeat it. [`prepare.py`](prepare.py) takes the `report_jobpart` table from Module 5 and copies it ten times, one copy per quarter, into `history.db`, which gives 2,000,000 rows. [`to_parquet.py`](to_parquet.py) then writes the same table to `report_history.parquet`. Parquet is a file format that stores each column together and compresses it, which is exactly what analytical queries like: the whole history fits in a **2.4 MB** file.

Before comparing anything, I wanted to be sure that both sides contain the same data, otherwise the race would mean nothing. My honesty check, [`check_sums.py`](check_sums.py), counts the rows and sums the prices on both sides:

| | SQLite (`history.db`) | Parquet |
|---|---:|---:|
| Rows | 2,000,000 | 2,000,000 |
| `SUM(part_price)` | 21,000,000.0 | 21,000,000.0 |
| Result | **MATCH** | |


## 2. The race, reported honestly

[`race.py`](race.py) runs the same queries on both engines, several times, alternating between them so that neither engine profits from a "warm" computer, and reports the median together with the range from the fastest to the slowest run ([`race-results.txt`](race-results.txt)):

| Query | SQLite (median) | DuckDB (median) | DuckDB faster by |
|---|---:|---:|---:|
| Dashboard aggregate | 280.7 ms (270.3–288.7) | 21.8 ms (20.7–29.4) | **12.9×** |
| Monthly report | 2,287.2 ms (2,214.2–2,342.6) | 51.8 ms (36.7–82.8) | **44.2×** |

I report the median instead of my best run because a single lucky run proves nothing, as I already saw in Module 3, when two identical runs gave me different times.


## 3. Reading `EXPLAIN ANALYZE`

The plan ([`plan.py`](plan.py), [`plan-results.txt`](plan-results.txt), and [`plan_sqlite.py`](plan_sqlite.py) for the SQLite side) explains *why* DuckDB is so fast for this kind of query. Unlike `EXPLAIN QUERY PLAN` in SQLite, `EXPLAIN ANALYZE` actually runs the query and shows how many rows passed through each step and how long each step took:

- DuckDB read only the **4 columns** the query needs (`machine_id`, `site`, `technician`, `part_price`) and skipped the other 3 completely; storing data by column makes that possible.
- The table scan read all **2,000,000 rows**.
- The operator that dominates is the **`HASH_GROUP_BY`**: it takes those 2,000,000 rows and groups them down to **350 rows**, and it is the most expensive step (about 0.68 s of the measured operator time).

SQLite, on the other hand, shows a `SCAN` over the full rows and a `USE TEMP B-TREE FOR GROUP BY`: it has to read every complete row, all 7 columns, even though it needs only 4.

## 4. Where DuckDB is the wrong engine

After seeing DuckDB win so clearly, I tested the opposite kind of work: many small single-row inserts, the kind of work an operational database does all day ([`boundary.py`](boundary.py), [`boundary_batched.py`](boundary_batched.py), [`boundary-results.txt`](boundary-results.txt)):

| 1,000 single-row inserts | Time |
|---|---:|
| SQLite | **1.8 ms** |
| DuckDB | **3,947.0 ms** |

Here DuckDB is roughly two thousand times slower. Batching the inserts helps DuckDB, but it does not close the gap. That is my number for where DuckDB is the wrong engine: writing one row at a time is OLTP work (transactions), not OLAP work (analysis), and an engine optimized for scanning whole columns pays a heavy price for every single small write.


## 5. What moves to the analytical copy, and how it stays fresh

I wrote my recommendation as a memo to Lea Winter and Yasmin Kaya ([`memo.md`](memo.md)). In short: the month-end report moves to the Parquet copy and is read with DuckDB, while SQLite stays the *system of record* for the operational work, new jobs, single-row writes and point lookups, because that is where it is fast.

An analytical copy is only useful if it is fresh. The Parquet file is rebuilt every night after the shift by running `to_parquet.py`. If that refresh silently stops, the dashboard would show numbers that are one day (or more) old, so the copy needs a check: comparing the latest `done_on` date in the Parquet file with the latest one in SQLite, and running `check_sums.py` on a schedule, would catch a refresh that stopped working.


---

## Reflection 6

What I took away from this module is in [Reflection 6](../Reflections/ref06.md).

**Where this leads:** this module showed me that one workload can need a different engine than another. [Module 6b](../Module06b/README.md) takes this idea further, comparing JSON, key-value storage and a real database server, and ending with a written decision about which engine to use for each job.
