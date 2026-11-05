"""Module 3 live demo - interactive menu. Run from the repo root: python Module03/demo.py"""
import sqlite3, statistics, time
from pathlib import Path

DB = Path(__file__).with_name("warehouse.db")
conn = sqlite3.connect(DB)
INDEXES = {"ix_orders_ordered_on": "CREATE INDEX ix_orders_ordered_on ON orders(ordered_on)",
           "ix_orderline_order":  "CREATE INDEX ix_orderline_order ON order_line(order_id)"}
LOOKUP = "SELECT o.order_id, o.ordered_on, c.name FROM orders o JOIN customer c ON c.customer_id = o.customer_id WHERE o.ordered_on = '2026-02-14'"
DASH = """SELECT c.city, COUNT(DISTINCT c.customer_id), SUM(ol.qty * p.price) AS revenue
FROM customer c JOIN orders o ON o.customer_id = c.customer_id
JOIN order_line ol ON ol.order_id = o.order_id JOIN product p ON p.product_id = ol.product_id
WHERE o.ordered_on >= '2025-01-01' AND o.ordered_on < '2026-01-01'
GROUP BY c.city ORDER BY revenue DESC"""

def reset():
    for ix in (*INDEXES, "ix_orderline_product"): conn.execute(f"DROP INDEX IF EXISTS {ix}")

def plan(sql):
    for r in conn.execute("EXPLAIN QUERY PLAN " + sql): print("     ", r[3])

def ms(sql, runs=3):
    t = []
    for _ in range(runs):
        t0 = time.perf_counter(); conn.execute(sql).fetchall(); t.append((time.perf_counter() - t0) * 1000)
    return statistics.median(t)

def demo_index():
    print("\nQUERY: all orders of ONE day.  First guess: SCAN or SEARCH?"); input("  (press Enter to reveal) ")
    reset(); print("  WITHOUT index:"); plan(LOOKUP); a = ms(LOOKUP); print(f"      median {a:.2f} ms")
    conn.execute(INDEXES["ix_orders_ordered_on"]); print("  WITH ix_orders_ordered_on:"); plan(LOOKUP); b = ms(LOOKUP)
    print(f"      median {b:.2f} ms  ->  about {a/b:.0f}x faster. The plan changed AND the clock agrees.")
    reset()

def demo_surprise():
    print("\nQUERY: 2025 revenue per city (touches ~2/3 of all rows).  Will an index on order_line help?")
    input("  (press Enter to reveal) ")
    reset(); print("  BASELINE:"); plan(DASH); a = ms(DASH); print(f"      median {a:.0f} ms")
    for k in INDEXES: conn.execute(INDEXES[k])
    print("  WITH both indexes:"); plan(DASH); b = ms(DASH); print(f"      median {b:.0f} ms")
    print(f"  -> {'SLOWER' if b > a else 'faster'} ({b/a:.1f}x). The plan changed; an index does not guarantee a speedup.")
    reset()

def demo_injection():
    print("\nType a customer name (blank = the classic payload  ' OR '1'='1  ).  Try  O'Brien  too.")
    name = input("  name> ") or "' OR '1'='1"
    try: rows = conn.execute(f"SELECT customer_id, name FROM customer WHERE name = '{name}'").fetchall(); print(f"  VULNERABLE (f-string): {len(rows)} rows returned", rows[:2])
    except sqlite3.Error as e: print("  VULNERABLE (f-string): CRASHED ->", e)
    rows = conn.execute("SELECT customer_id, name FROM customer WHERE name = ?", (name,)).fetchall()
    print(f"  SAFE (bound parameter): {len(rows)} rows returned", rows[:2])

def demo_algebra():
    print("""\n  SQL      : SELECT o.order_id, o.ordered_on, c.name FROM orders o JOIN customer c ON ... WHERE o.ordered_on = '2026-02-14'
  ALGEBRA  : pi_{order_id, ordered_on, name}( sigma_{ordered_on='2026-02-14'}( orders JOIN_{customer_id} customer ) )
  MAPPING  : sigma = WHERE | pi = SELECT list | JOIN = JOIN ... ON""")

MENU = {"1": ("Plan + index: SCAN becomes SEARCH", demo_index), "2": ("The index that made it SLOWER", demo_surprise),
        "3": ("SQL injection: break it, then fix it", demo_injection), "4": ("Algebra <-> SQL", demo_algebra)}
if __name__ == "__main__":
    reset()
    try:
        while True:
            print("\n=== Module 3 demo ===");  [print(f" {k}) {v[0]}") for k, v in MENU.items()]
            c = input(" q) quit > ").strip().lower()
            if c == "q": break
            if c in MENU: MENU[c][1]()
    finally:
        reset(); conn.close()
