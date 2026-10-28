"""Demonstrate why bound parameters matter.

Run with:  uv run python module-01/bound-parameters-demo.py
"""
import sqlite3

# Create an in-memory database (goes away when the script ends)
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE readings(machine TEXT, temp_c REAL)")

# ------------------------------------------------------------
# ❌ DANGEROUS: string concatenation (DON'T do this)
# ------------------------------------------------------------
print("=== Dangerous: string concatenation ===")

# Imagine a user types this as the machine name
user_input = "cnc-01', 99.9); DROP TABLE readings; --"

# If we glue it into the SQL, the whole table gets dropped!
dangerous_sql = f"INSERT INTO readings VALUES ('{user_input}', 42.0)"
print("SQL that would be executed:")
print(dangerous_sql)

try:
    conn.execute(dangerous_sql)
    print("Executed (bad!). Table gone?")
    print(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
except sqlite3.Error as e:
    print("Error:", e)

# ------------------------------------------------------------
# ✅ SAFE: bound parameters (DO this)
# ------------------------------------------------------------
print()
print("=== Safe: bound parameters ===")

# Recreate the table in case it was dropped
conn.execute("CREATE TABLE IF NOT EXISTS readings(machine TEXT, temp_c REAL)")

# Same malicious input, but passed as a value, not as SQL
user_input = "cnc-01', 99.9); DROP TABLE readings; --"

safe_sql = "INSERT INTO readings VALUES (?, ?)"
print("SQL executed:", safe_sql)
print("Values passed separately:", (user_input, 42.0))

conn.execute(safe_sql, (user_input, 42.0))
conn.commit()

# The table still exists, and the value is stored literally
print("Table still exists:", conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print("Rows in readings:", conn.execute("SELECT machine, temp_c FROM readings").fetchall())

conn.close()
