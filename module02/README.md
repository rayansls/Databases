# Module 02 — Data Contracts & Reading Legacy Schemas (ERD Audits)

**Course placement:** Session 2. This module covers the conceptual database design
and requirements analysis chapters — but from the direction real engineers meet them:
you inherit a schema that already exists and must reconstruct what it means.

## Learning Goals

By the end of this module, you can:

- **Reconstruct an ER/EER model** (entities, attributes, keys, relationships, cardinalities)
  from an undocumented SQL schema.
- **Identify integrity defects** — missing foreign keys, orphan rows, redundant data,
  normalization violations — with queries, not intuition.
- **Distinguish** an entity relationship from an attribute, and a surrogate key from a
  natural key, and justify the choice.
- **Express a schema as a code-first data contract** (Pydantic / SQLAlchemy) that an
  application can enforce.
- **Write the requirements the schema forgot**: the business rules nobody encoded.

---

## What I did to reach these goals

### Reconstruct the ER model from a broken legacy schema

I started from `legacy.db`, a deliberately flawed database from a fictional
plastics-injection-molding plant (Kortmann Kunststofftechnik GmbH). It has three tables
(`machine`, `part`, `maint_job`), **no primary keys**, **no foreign keys**, **no UNIQUE
constraints**, prices stored as TEXT, dates stored as TEXT (including `'unknown'`), and
a comma-separated list of part numbers in `maint_job.parts_used`.

I read the `CREATE TABLE` statements and reconstructed the model the designer **meant**:

| Entity | Attributes | Intended PK |
|---|---|---|
| **Machine** | serial_no, site, installed | `serial_no` (natural) + surrogate `machine_id` |
| **Part** | part_no, description, unit_price | `part_no` (natural) |
| **MaintenanceJob** | job_id, done_on | `job_id` (surrogate) |
| **Technician** | name | `technician_id` (surrogate) — *not modelled in the legacy schema* |
| **JobPart** | job_id, part_no | composite `(job_id, part_no)` — *not modelled; hidden in `parts_used`* |

Two key observations:

- **`technician` was demoted to a TEXT column.** The designer meant it as an entity, but
  the schema treats it as an attribute. This is exactly the "entity vs. attribute"
  ambiguity the module asks me to notice.
- **`parts_used` is a many-to-many list hidden in a column.** The junction table
  (`job_part`) that should hold the m:n relationship was never created.

I drew the reconstructed ER diagram in Mermaid (rendered with mermaid.live) and saved it
as `pictures/er-diagram.png`. The diagram shows the five entities and the three
relationships: `Machine 1:n MaintenanceJob`, `Technician 1:n MaintenanceJob`, and
`MaintenanceJob m:n Part` (via the `JobPart` junction).

### Prove the cardinalities with COUNT queries

The module's tip is: *"the fastest way to find the real cardinality is to count distinct
values."* I applied this to prove that `parts_used` is really an m:n list:

```sql
SELECT job_id, parts_used,
       LENGTH(parts_used) - LENGTH(REPLACE(parts_used, ',', '')) + 1 AS n_parts
FROM maint_job;
## Reflection 3
[Reflection 3](/Reflections/ref03.md)


