DROP TABLE IF EXISTS flat_jobpart;
CREATE TABLE flat_jobpart (
    job_id      INTEGER,
    machine_id  TEXT,
    site        TEXT,
    technician  TEXT,
    part_no     TEXT,
    part_price  TEXT,
    done_on     TEXT
);

WITH RECURSIVE j(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM j WHERE n < 20000),
               p(k) AS (SELECT 1 UNION ALL SELECT k+1 FROM p WHERE k < 10)
INSERT INTO flat_jobpart
SELECT n,
       'cnc-' || printf('%02d', (n % 50) + 1),
       CASE (n % 50) WHEN 0 THEN 'Bielefeld' ELSE 'Gütersloh' END,
       'tech-' || (n % 7),
       'P-' || printf('%04d', (k % 40) + 1),
       printf('%.2f', 5 + (k % 40)),
       date('2026-01-01', '+' || (n % 90) || ' days')
FROM j CROSS JOIN p;

CREATE INDEX ix_flat_machine ON flat_jobpart(machine_id);

DROP TABLE IF EXISTS job_part;
DROP TABLE IF EXISTS job;
DROP TABLE IF EXISTS part;
DROP TABLE IF EXISTS machine;

CREATE TABLE machine(
    machine_id TEXT PRIMARY KEY,
    site       TEXT NOT NULL
);
CREATE TABLE part(
    part_no    TEXT PRIMARY KEY,
    part_price REAL NOT NULL
);
CREATE TABLE job(
    job_id     INTEGER PRIMARY KEY,
    machine_id TEXT NOT NULL REFERENCES machine(machine_id),
    technician TEXT NOT NULL,
    done_on    TEXT NOT NULL
);
CREATE TABLE job_part(
    job_id  INTEGER REFERENCES job(job_id),
    part_no TEXT    REFERENCES part(part_no),
    PRIMARY KEY (job_id, part_no)
);

INSERT INTO machine SELECT DISTINCT machine_id, site FROM flat_jobpart;
INSERT INTO part    SELECT DISTINCT part_no, CAST(part_price AS REAL) FROM flat_jobpart;
INSERT INTO job     SELECT DISTINCT job_id, machine_id, technician, done_on FROM flat_jobpart;
INSERT INTO job_part SELECT DISTINCT job_id, part_no FROM flat_jobpart;