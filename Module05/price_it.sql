.timer on

-- Change one machine's site in the 3NF design
UPDATE machine SET site = 'Bielefeld' WHERE machine_id = 'cnc-02';
SELECT changes() AS rows_changed_in_machine;

-- Change the same machine's site in the Denormalized design
UPDATE report_jobpart SET site = 'Bielefeld' WHERE machine_id = 'cnc-02';
SELECT changes() AS rows_changed_in_report;

-- Storage check (in bytes)
SELECT 'normalized (4 tables)' AS design, SUM(pgsize) AS bytes FROM dbstat WHERE name IN ('job','job_part','part','machine');
SELECT 'denormalized (report_jobpart)' AS design, SUM(pgsize) AS bytes FROM dbstat WHERE name = 'report_jobpart';