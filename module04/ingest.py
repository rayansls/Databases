import csv
import sqlite3

def ingest(csv_path, db_path="edge.db"):
    conn = sqlite3.connect(db_path)
    # Dobbiamo dire a Python di accendere la FK per questa connessione!
    conn.execute("PRAGMA foreign_keys = ON")
    
    sql = """
    INSERT INTO reading(sensor_id, ts, value, interval_s)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value
    """
    
    with open(csv_path) as f:
        rows = [(int(r["sensor_id"]), r["ts"], float(r["value"]), int(r["interval_s"]))
                for r in csv.DictReader(f)]
                
    conn.executemany(sql, rows)
    conn.commit()
    
    n = conn.execute("SELECT COUNT(*) FROM reading").fetchone()[0]
    conn.close()
    return n

if __name__ == "__main__":
    print(f"Rows in database after ingest: {ingest('readings.csv')}")
