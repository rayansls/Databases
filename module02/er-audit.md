# ER Audit — legacy.db

## Entities, attributes, intended primary keys

### Machine
- Attributes: machine_name, serial_no, site, installed
- Intended PK: `serial_no` (natural key — machine_name is not stable, see `RANDOM-NAME`)
- Note: surrogate PK `machine_id` should be added; keep `UNIQUE(serial_no)`

### Part
- Attributes: part_no, description, unit_price
- Intended PK: `part_no` (natural key)
- Note: UNIQUE constraint missing → P-1003 duplicated in seed data

### MaintenanceJob
- Attributes: job_id, machine_name, technician, done_on, parts_used
- Intended PK: `job_id` (surrogate)
- Note: `machine_name` should be `machine_id` (FK); `parts_used` is a 1NF violation

### Technician
- **Not modelled at all** — the schema demotes it to a TEXT column `technician`.
- Intended PK: `technician_id` (surrogate); natural key: `name` (with UNIQUE)

### JobPart (junction)
- **Not modelled** — hidden inside `parts_used` as a comma-separated list
- Intended PK: composite `(job_id, part_no)`

## Cardinalities the legacy schema models vs. hides

- **1:1** — Not modelled anywhere. No 1:1 relationship exists in this schema, and none is needed.
- **1:n** — Hidden. `maint_job.machine_name` is a text column, not a declared FK, so Machine → Job is 1:n **by convention** but not enforced.
- **m:n** — Hidden inside `parts_used`, a comma-separated list. The junction table (JobPart) is missing entirely.

## Defect 1 — Orphan maintenance jobs
Query:
    SELECT m.job_id, m.machine_name FROM maint_job m
    LEFT JOIN machine x ON m.machine_name = x.machine_name
    WHERE x.machine_name IS NULL;
Result: `3|cnc-05`
Production impact: job 3 references machine `cnc-05`, which does not exist. Reports by machine or site silently drop or misattribute it.

## Defect 2 — Duplicate natural key
Query:
    SELECT part_no, COUNT(*) AS copies FROM part
    GROUP BY part_no HAVING COUNT(*) > 1;
Result: `P-1003|2`
Production impact: `P-1003` is duplicated because `part_no` has no UNIQUE constraint. Any aggregation double-counts it silently.

## Defect 3 — Text price comparison
Query:
    SELECT part_no, unit_price FROM part WHERE unit_price < '15';
Result: only `P-1001|'12.50'` — `P-1003` (€9.90) is silently EXCLUDED because as text `'9.90' > '15'` (first character `'9' > '1'`).
Production impact: `unit_price` is TEXT, so comparisons are lexicographic, not numeric. A filter like `< '15'` silently drops the cheapest parts. Invoices, alerts, and price reports are wrong — with no error.
Also note: the value displays as `'12.50'` with quotes — SQLite is telling you it's a string, not a number.

## Defect 4 — Installed dates that are not dates
Query:
    SELECT machine_name, installed FROM machine
    WHERE installed NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]';
Result: `RANDOM-NAME|unknown`
Production impact: `installed` is free TEXT. Row `RANDOM-NAME` has `'unknown'`. Any date filter silently drops or breaks on this row; age/warranty calculations fail.

## Cardinality proof
Query:
    SELECT job_id, parts_used,
           LENGTH(parts_used) - LENGTH(REPLACE(parts_used, ',', '')) + 1 AS n_parts
    FROM maint_job;
Result: job 1 → 2 parts; job 2 → 1 part; job 3 → 1 part; job 4 → NULL
Conclusion: `parts_used` is a many-to-many list hidden in a TEXT column. Job 1 is the proof.
## Constraint placement — application vs. database

- **Pydantic (application layer):** `serial_no` prefix rule (`SN-`), positive `machine_id`. These are *business rules* — the DB doesn't know what a serial is.
- **SQLAlchemy / DB (structural layer):** PRIMARY KEY, FOREIGN KEY, UNIQUE(serial_no), NOT NULL, NUMERIC(9,2). These must hold for *every* client, not just this application.