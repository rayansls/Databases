# Bound parameters — why they matter

## The dangerous way

```python
cursor.execute("INSERT INTO readings VALUES ('" + ts + "', '" + machine + "')")
```

The data is glued into the SQL string. If a value contains a quote `'` or
malicious SQL, the query breaks — or worse, executes arbitrary SQL. This is
called **SQL injection**.

## The safe way

```python
cursor.execute("INSERT INTO readings VALUES (?, ?)", (ts, machine))
```

The `?` is a placeholder. The values are passed separately and treated as
**data**, never as code. No matter what the input contains, it cannot become SQL.

## Proof

See `bound-parameters-demo.py`. It shows that the same malicious input:
- **breaks or executes arbitrary SQL** when used with string concatenation
- **is stored literally** when used with bound parameters

Run output from the demo:

```
=== Dangerous: string concatenation ===
INSERT INTO readings VALUES ('cnc-01', 99.9); DROP TABLE readings; --', 42.0)
Error: You can only execute one statement at a time.

=== Safe: bound parameters ===
SQL executed: INSERT INTO readings VALUES (?, ?)
Values passed separately: ("cnc-01', 99.9); DROP TABLE readings; --", 42.0)
Table still exists: [('readings',)]
Rows in readings: [("cnc-01', 99.9); DROP TABLE readings; --", 42.0)]
```

## Where I used this

In `load_telemetry.py`:

```python
conn.executemany("INSERT INTO readings VALUES (?, ?, ?, ?, ?)", rows)
```

Five `?` for five columns — 172,800 rows loaded safely.