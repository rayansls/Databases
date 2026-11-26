# Module 6b — Polyglot Persistence & the Decision

[← Module 6a](../Module06a/README.md) · [Back to my portfolio](../README.md) · [Reflection 7](../Reflections/ref07.md)

In Module 6a I learned that one engine can be perfect for one job and terrible for another: DuckDB was almost 13 times faster for the month-end report and about two thousand times slower for small single-row writes. This module takes that idea to the whole plant. Kortmann has four different workloads: the machines constantly append new readings, the month-end report reads two years of history, the vendor metadata keeps growing new fields, and the dashboard needs to remember who logged in and which filter they used last. One engine *could* serve all four, but not equally well. So the goal of this module was not to learn as many engines as possible, but to make a decision for each workload, write it down on one page, and defend it with numbers I actually produced.

## Learning goals

1. Store **semi-structured data (JSON)** in SQLite and query it with `json_extract`/`json_each` and an **expression index**.
2. Implement and evaluate a **key-value access pattern** against SQLite.
3. Explain **ACID vs. BASE** and the **CAP theorem** in terms of the systems you actually ran.
4. Choose an engine per workload and **defend the choice with a measurement**.
5. Say what changes — and what gets harder — when the same data lives on a **server**.

My evidence for this module: [`json_bench.py`](json_bench.py) (Task 2), [`kv_compare.py`](kv_compare.py) (the key-value homework), [`two_writers.py`](two_writers.py) (the SQLite version of Task 1), the [decision record](#4-the-decision-record) below, and the [project ticket](project-ticket.md).

---

## 1. Vendor metadata as JSON, and the index that disappears

The first problem belongs to Anke Reuter, who maintains the machine records. Every vendor sends different information, a calibration date here, a firmware version there, sometimes nothing at all, and until now every new field meant changing the table and stopping the system for a maintenance window. Her sentence was: *"I don't need a schema for fields I don't know yet."*

The solution I tried is a middle path. The machine stays a normal row in a relational table, but everything the vendor sends goes into one column, `meta`, as a JSON document. To make sure that column really contains JSON and not random text, I added the same kind of rule as in [Module 4](../module04/README.md): `CHECK (json_valid(meta))`. When I tried to insert the text `not json at all`, the database refused it with `CHECK constraint failed: json_valid(meta)`.

Reading the data back turned out to be simple. `json_extract(meta, '$.vendor')` treats a path inside the document as if it were a normal column, and `json_each` turns a whole document into rows, so for `cnc-01` I got three rows: vendor Siemens, firmware 4.2, and the calibration date. I could also still ask questions across all machines with plain SQL, for example how many devices have no calibration date at all (998 of 1,000).

The most important moment was the index. Since the plant filters by vendor, I created an index on exactly that expression, and then compared two queries that ask the same question:

| Query | Plan |
|---|---|
| `WHERE json_extract(meta, '$.vendor') = 'Fanuc'` | `SEARCH device USING INDEX ix_device_vendor (<expr>=?)` |
| `WHERE meta ->> 'vendor' = 'Fanuc'` | `SCAN device` |

Both queries return the same 334 devices, but only the first one uses the index. **The `->>` version loses the index because an expression index only matches the exact expression it was built on, and for SQLite `meta ->> 'vendor'` is a different expression from `json_extract(meta, '$.vendor')`, even though it gives the same answer.** It is the same lesson I learned in [Module 3](../Module03/README.md) with `lower(technician)`: anything that changes the expression around a column hides it from the index. The module notes say this is the most common LLM mistake with JSON columns, and now I understand why it is so easy to make.

What JSON costs: I lose the column types (the database no longer knows that a calibration date is a date), and joining on values inside the JSON is not cheap. What it buys: Anke can store new vendor fields tomorrow without changing the table. To me this showed that "NoSQL" does not mean "no schema": a JSON column with `json_valid`, an index on the paths I filter on and a list of the keys I expect *is* a schema, just a more flexible one.

## 2. Dashboard sessions: key-value or SQLite?

The second problem comes from Yasmin Kaya. The dashboard remembers, for each session, who is logged in and which filter they used last. That is a lookup by one key and nothing else, so her question was fair: *"Do we really run that through a relational engine?"*

To answer it I ran [`kv_compare.py`](kv_compare.py), which stores and reads back 20,000 sessions twice: once in Python's `shelve`, a simple key-value store, and once in a SQLite table with the session key as the primary key.

| 20,000 sessions | write | read |
|---|---:|---:|
| `shelve` (key-value) | ~3.5 s | ~0.1 s |
| SQLite (`session` table) | ~0.03 s | ~0.07 s |

[TODO: re-run `uv run python Module06b/kv_compare.py` on my laptop and replace these numbers with my own. `shelve` uses a different backend on every platform, so the module asks for orders of magnitude, not decimals.]

Reading is in the same order of magnitude in both, a few microseconds per session. Writing is where they differ, and on this run SQLite was about a hundred times faster, because `executemany` writes all 20,000 sessions in a single transaction, while `shelve` stores them one by one. So the key-value store did not win even on the one job it was designed for.

And there is one thing SQLite can do that `shelve` simply cannot: ask a question across all sessions. With one `GROUP BY` I could count how many sessions used each city filter (5,000 each). With `shelve` I can only fetch one key at a time, so I would have to read every single session and count them myself in Python. For this reason I would ship the dashboard sessions as a small key-value table *inside* SQLite: it is as simple as a key-value store, and it keeps the possibility to ask questions later.

## 3. ACID, BASE and CAP, in the systems I actually ran

These three words sounded very abstract to me, so I tried to connect each one to something I saw myself.

**ACID** is what one transaction guarantees: it happens completely or not at all (*atomicity*), the rules still hold afterwards (*consistency*), two transactions do not see each other's half-finished work (*isolation*), and once it is committed it survives a crash (*durability*). The easiest picture for me is a bank transfer. I saw isolation directly in [`two_writers.py`](two_writers.py): while writer A had an open transaction on the `machine` row, writer B was refused with `database is locked`, and only after A committed could B write. The final count was 2, so no update was lost. I saw consistency in [Module 4](../module04/README.md), where the constraints refused every bad row, and atomicity in my Module 4 ingest script, where a reading is either stored completely or not at all, never half of it.

**BASE** is the opposite philosophy, used on purpose by large distributed systems: *basically available*, *soft state*, *eventually consistent*. The picture is a social media feed, where a like may appear a few seconds late and then catch up. None of the systems I ran in this course is BASE, and that is exactly the point: everything I used lives on one machine.

**CAP** is about what a distributed system has to choose when the network between its machines breaks: either it stays *consistent* (it gives the correct answer or refuses to answer) or it stays *available* (it always answers, even with possibly old data). It is not "pick two out of three" all the time; it is a choice that only appears when the network fails. SQLite never has to make this choice, because it does not distribute: it is ACID on one machine. The PostgreSQL server from Task 1 is also one machine, so if it stops, it does not answer with old data: every client simply fails.

## 4. The decision record

This is the one-page decision for Kortmann. Every row is based on a measurement or an observation from this course, not on an opinion.

| Workload | Engine | Why | Evidence | Cost accepted | What breaks if stale/missing? |
|---|---|---|---|---|---|
| Month-end report over two years | Parquet + DuckDB | A 2M-row aggregate is much faster in a column engine, and the operational SQLite stays free for writing | [Module 6a](../Module06a/README.md): dashboard 280.7 ms → 21.8 ms (12.9×), monthly report 2,287 ms → 52 ms (44×); Parquet file 2.4 MB; row count and sums match | A nightly export and up to one day of staleness | Rebuild the Parquet file; the report shows the last complete day |
| Sensor/job ingest, every 30 s, a crash must not lose rows | SQLite | Embedded and ACID: a committed row survives a crash, and constraints refuse garbage at the edge | [Module 4](../module04/README.md): `ingest.py` run twice → still 4 rows (idempotent UPSERT); NOT NULL, CHECK and FOREIGN KEY reject bad rows; [Module 6a](../Module06a/README.md): 1,000 single-row inserts in 1.8 ms (DuckDB: 3,947 ms) | One writer at a time; foreign keys must be switched on in every connection | Missing rows mean missing alarms; a device that resends data creates no duplicates |
| Vendor metadata that gains fields | SQLite with a JSON column | New vendor fields need no migration, while the machine row and its joins stay relational | [`json_bench.py`](json_bench.py): `json_valid` rejects non-JSON; the expression index gives `SEARCH ... USING INDEX`, the `->>` version gives `SCAN` | No column types inside the JSON; queries must use exactly the indexed expression | An unknown field is simply stored; a missing field returns NULL, so a missing calibration date has to be checked on purpose |
| Dashboard session state | SQLite key-value table (`k TEXT PRIMARY KEY, v TEXT`) | It is a lookup by one key, and SQLite is as fast as `shelve` for reading and much faster for writing, while still allowing queries across sessions | [`kv_compare.py`](kv_compare.py): reads ~0.1 s for 20,000 sessions in both; writes ~0.03 s (SQLite) vs ~3.5 s (`shelve`) [TODO: my laptop numbers] | Slightly more setup than a dictionary | Users lose their last filter and have to log in again; no business data is lost |
| *(optional)* Concurrent users on the network | PostgreSQL server, only if many people must write at the same time from different machines | SQLite allows one writer at a time on one file; a server handles many connections | [`two_writers.py`](two_writers.py): the second writer gets `database is locked`; my observations in section 5 | Credentials, network, operations, and a single point of failure | If the server is down, every client fails at once |

**If Kortmann could run only one engine, it would be SQLite.** It handles three of the four workloads well (ingest, vendor metadata and sessions), it needs no server, and it is ACID on the machine where the data is created. What would break first is the month-end report: in Module 6a SQLite needed 280.7 ms for the dashboard and about 2.3 seconds for the monthly report on 2,000,000 rows, where DuckDB needed 22 ms and 52 ms, and that gap grows with every month of history. The report would not become wrong, it would become slow, and while it runs it competes with the writer for the same file.

### Defence notes

Since I was not in class, I could not swap records with another pod, so I asked myself the four questions the listening pod would have asked:

- **Which row has no measurement behind it?** The concurrent-users row has no server measurement of my own, only the SQLite lock from `two_writers.py`. That is why I kept it optional.
- **Where does my choice duplicate data, and who updates it?** Only in the report row: the Parquet file is a copy of the SQLite data, and the nightly `to_parquet.py` run updates it, with `check_sums.py` as the check that the copy is complete.
- **What breaks if two people write at the same time?** With SQLite, the second writer waits or gets `database is locked`; nothing is lost, but writes happen one after the other. If the plant ever has many writers on the network, that is the row where I would switch to a server.
- **Why is this a database and not three spreadsheets?** Because the database refuses bad data (constraints, `json_valid`), lets me ask questions across all the rows (how many devices are not calibrated, how many sessions use each filter) and keeps a committed row safe after a crash.

The row I would change after this exercise is the session-state row: at first I expected a key-value store to be the natural choice, but my own benchmark showed that a key-value table inside SQLite is just as good, so I moved it to SQLite.

## 5. What changes when the data lives on a server

I missed this session because of a doctor's appointment, so I could not take part in the shared-server task, where each pod had one database on a shared PostgreSQL server and used it through pgweb in the browser. Instead I did the fallback that the module itself describes for when the server is not available: [`two_writers.py`](two_writers.py) opens two connections to the same SQLite file and lets both write to the same row at the same time. Writer A starts a transaction with `BEGIN IMMEDIATE` and does not commit yet; writer B immediately gets `database is locked`, and only after A commits can B write. The final count is 2, so no update was lost. My three observations come from this experiment and from the module description of the server task:

- **Easier:** with a server, many people on different devices can connect to the same database at the same time, and the server puts conflicting writes in line. With SQLite everyone has to share one file on one machine, and the second writer simply gets `database is locked`.
- **Harder:** before writing a single query you need a host, a port, a user, a password and the right SSL setting, and some SQL is different: PostgreSQL has no `STRICT` and no `PRAGMA`, and an `INTEGER PRIMARY KEY` does not count up by itself, so `machine_id` has to be given explicitly.
- **A new failure mode:** if the database process stops, every client fails at the same moment, and nothing in your SQL can fix it. An embedded database cannot have this problem, because there is no separate process and no network between the program and the data: if my program runs, the database runs.

This is also why the server row in my decision record is optional. A server adds concurrent connections, which is good, but also network failures, credentials, operations and latency, which are all new problems. It makes conflicting writes wait in line, but it does not fix a read-modify-write mistake in my own code, and one server is still one single point of failure. For me, local-first remains the default, and a server is something I choose only when a measured requirement, like many writers on the network, really needs it.

---

## Reflection 7

What I took away from this module is in [Reflection 7](../Reflections/ref07.md).

**Where this leads:** this module ends the technical part of the course with a decision instead of a new tool. In the final project my team starts again from a person and a first question, and the [project ticket](project-ticket.md) is where that begins.
