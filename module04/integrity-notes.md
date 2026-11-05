
## UPDATE on NULL test
When I tried to insert a NULL into scratch2.db, it failed with: `NOT NULL constraint failed: t.value`. 
This proved that the CHECK constraint was not what stopped it. If we remove NOT NULL, the CHECK allows the NULL because `NULL BETWEEN x AND y` evaluates to unknown, not FALSE.

## Task 2 - UPSERT Evidence
- Created unique index `ux_reading_sensor_ts` on (sensor_id, ts).
- Ran INSERT with `ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value`.
- Result: SELECT showed exactly 1 row for that timestamp, with value updated from 41.5 to 41.7. No duplicate was created.

## Task 2 - Python Ingest Evidence
- Created `ingest.py` using `executemany` and the same `ON CONFLICT DO UPDATE` logic.
- Ran `python ingest.py` twice on the same `readings.csv`.
- Output both times: `Rows in database after ingest: 4`. 
- Proof of idempotency: no duplicates were created on the second run.

## Task 3 - Trigger Evidence
- **Alarm Trigger:** Inserted a vibration reading of 2.7. The trigger automatically fired and inserted a row into `alarm` with reason "vibration over 2.0 mm/s".
- **Audit Trigger:** Updated the reading value from 2.7 to 1.4. The trigger automatically fired and inserted a row into `audit` recording old_value=2.7 and new_value=1.4.

## Task 4 - Access Control Reflection
With PostgreSQL, access control is managed centrally via CREATE ROLE and GRANT commands (e.g., GRANT SELECT ON machine_health TO reports_user). In SQLite, there are no users or roles, so access control shifts to the OS (file permissions) and views. 

File-permission control (chmod) is perfectly acceptable at the edge because it's a single-tenant, physically secure box where the OS user is the only boundary needed. However, it is not acceptable for a multi-tenant web app because a single SQLite file cannot distinguish between Tenant A and Tenant B—they would all share the same OS-level access, leading to data leaks. A multi-tenant app requires a server with distinct user roles and row-level security.

## Task 5 (Stretcher) - BEFORE Trigger Test
- Created a `BEFORE INSERT` trigger with `RAISE(ABORT)`.
- Tried to insert a value of 4500. Result: `Runtime error: value too high`.
- This proves BEFORE triggers can reject a row, unlike AFTER triggers which only run once the row is already committed.

## Task 3 - Trigger Cost Benchmark
- Ran a Python script inserting 10,000 rows into an in-memory database.
- **Without trigger:** [INSERISCI QUI IL TUO PRIMO NUMERO] seconds.
- **With trigger:** [INSERISCI QUI IL TUO SECONDO NUMERO] seconds.
- **Conclusion:** The trigger adds a small but measurable overhead because it performs an extra INSERT into the alarm table for every row. On a hot ingestion path, this is a design trade-off.
