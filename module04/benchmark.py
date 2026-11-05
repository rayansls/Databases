import sqlite3
import time

def run_test(use_trigger, n=10000):
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("CREATE TABLE sensor(sensor_id INTEGER PRIMARY KEY, machine_id TEXT, metric TEXT)")
    conn.execute("INSERT INTO sensor VALUES (1, 'm1', 'vib_rms')")
    conn.execute("CREATE TABLE reading(sensor_id INTEGER, ts TEXT, value REAL)")
    conn.execute("CREATE TABLE alarm(alarm_id INTEGER PRIMARY KEY, sensor_id INTEGER, ts TEXT, value REAL)")
    
    if use_trigger:
        conn.execute("""
            CREATE TRIGGER trg_vib_alarm AFTER INSERT ON reading
            FOR EACH ROW WHEN NEW.value > 2.0
            BEGIN
                INSERT INTO alarm(sensor_id, ts, value) VALUES (NEW.sensor_id, NEW.ts, NEW.value);
            END;
        """)
    
    start = time.perf_counter()
    for i in range(n):
        conn.execute("INSERT INTO reading VALUES (1, '2026-03-01', 2.5)")
    conn.commit()
    end = time.perf_counter()
    conn.close()
    return end - start

print(f"Tempo SENZA trigger (10.000 righe): {run_test(False):.4f} secondi")
print(f"Tempo CON trigger (10.000 righe):   {run_test(True):.4f} secondi")
