# Module 4 — Data Integrity, Constraints & Edge Triggers

[← Module 3](../Module03/README.md) · [Back to my portfolio](../README.md) · [Reflection 4](../Reflections/ref04.md) · [Next: Module 5 →](../Module05/README.md)

In Module 3 I checked whether the queries I received were right. In this module the question moved one step earlier: is the *data* right in the first place? The story is about the edge, a small computer next to the machines on the shop floor, where sensor readings arrive all day and nobody is there to watch them. At the edge there is no database administrator to save you, so the database has to be a little paranoid: it should refuse garbage on its own, instead of trusting every program that writes to it. My notes and evidence are in [`integrity-notes.md`](integrity-notes.md).

## Learning goals

1. Create tables with the full constraint toolkit: `NOT NULL`, `UNIQUE`, `CHECK`, `PRIMARY KEY`, `FOREIGN KEY`, and `STRICT` typing.
2. Use **generated columns** to derive values at the engine instead of in application code.
3. Write **triggers** that enforce domain rules and maintain audit/rollup tables automatically.
4. Use **DML** correctly — including `UPSERT` (`ON CONFLICT`) for idempotent edge ingestion.
5. Reason about **access control (DCL)**: who may read or write, and how that maps from server `GRANT`s to an embedded, local-first world.

---

## 1. The constraint toolkit, and seeing each rule say no

I started with the "before" picture: a table with no constraints at all, into which I inserted three obviously wrong rows. All three landed without a single complaint, including text in a number column. After that, every constraint I added had to prove itself the same way, by rejecting something. My rule for this module became: *a constraint is only real if I have seen its error message.*

Two moments taught me the most:

- **CHECK does not stop NULL.** I expected my `CHECK` on the value range to reject a missing value, but the error I actually got was `NOT NULL constraint failed: t.value`. The reason is that a `CHECK` only rejects a row when its condition is FALSE, and `NULL BETWEEN x AND y` is not false, it is *unknown*, so without `NOT NULL` the empty value would slip through.
- **Foreign keys are off by default.** My insert for a sensor that does not exist (sensor 99) went through without any error, and for a moment I thought I had broken my schema. Then I understood that `PRAGMA foreign_keys = ON` only lives in the connection where you set it, and every new `sqlite3` command opens a fresh connection where foreign keys are OFF again. When I put the PRAGMA inside the same script, the `FOREIGN KEY constraint failed` error finally appeared.

I also learned to always check the schema after creating a table: a copy-paste error had corrupted my `CHECK` line, and the table still *looked* fine until I read it back with `.schema`.


## 2. Generated columns

A generated column is a column whose value the database calculates by itself from other columns, for example a temperature in Fahrenheit computed from the Celsius value, so that no application can ever store a wrong or outdated version of it.


## 3. Triggers for alarms and audit

A trigger is a small rule that the database runs automatically when something happens to a table. I wrote two of them:

- An **alarm trigger**: when I inserted a vibration reading of 2.7, the database added a row to the `alarm` table on its own, with the reason "vibration over 2.0 mm/s".
- An **audit trigger**: when I changed that reading from 2.7 to 1.4, the database recorded the old and the new value in the `audit` table, so the change can never happen silently.

In the stretcher I also tried a `BEFORE INSERT` trigger with `RAISE(ABORT)`: inserting a value of 4500 was rejected with `value too high`. This showed me the difference between the two kinds of trigger: an `AFTER` trigger reacts to a row that has already been written, while a `BEFORE` trigger can stop the row from being written at all.

Finally I measured whether triggers make inserts slow, with [`benchmark.py`](benchmark.py), which inserts 10,000 rows with and without the alarm trigger. The trigger only added a few hundredths of a second, which changed how I think about them: a trigger is not automatically "slow", it depends on what it does, although on a very busy ingestion path even a small extra cost is a design decision.



## 4. UPSERT: ingesting the same data twice without duplicates

At the edge the network can drop at any moment, so a device often sends the same readings again. If every repeat became a new row, the data would slowly fill up with duplicates. The answer is to make ingestion **idempotent**, which means that running it twice gives the same result as running it once.

I created a unique index on `(sensor_id, ts)`, so that one sensor can have only one reading per timestamp, and then used `INSERT ... ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value`. When the same timestamp arrived with a corrected value, the row was updated from 41.5 to 41.7 instead of being duplicated. Then I wrote [`ingest.py`](ingest.py), which loads [`readings.csv`](readings.csv) with `executemany`, bound parameters and the same `ON CONFLICT` rule, and ran it twice: both times the database contained exactly 4 rows. Seeing that number stay the same was the most satisfying moment of the module, because it felt like building something that really survives a network outage.

## 5. Access control without a server

A server database like PostgreSQL manages access centrally, with users and roles (`CREATE ROLE`, `GRANT SELECT ON machine_health TO reports_user`). SQLite has none of that: there are no users and no roles, so access control moves to the operating system (who is allowed to read or write the file) and to views (which expose only a safe part of the data).

My conclusion is that file permissions are perfectly fine at the edge, because it is a single box, physically secured, with one user, so the operating system is the only boundary needed. They are not acceptable for a web app with many customers, because one SQLite file cannot tell customer A from customer B: everyone with access to the file sees everything. That situation needs a server with separate roles and row-level security.


---

## Reflection 4

My three golden rules from this module, and the full story of the foreign-key problem, are in [Reflection 4](../Reflections/ref04.md).

**Where this leads:** constraints make each row correct. In [Module 5](../Module05/README.md) the question is how to arrange the tables themselves: how much to split them apart so that every fact is stored only once, and when it is worth copying data on purpose to make reading faster.
