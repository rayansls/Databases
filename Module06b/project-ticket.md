# Project ticket

[← Module 6b README](README.md)

The final project starts from a person and a first question, not from a technology. Our Project Team chose **MACHINEX**, a machine-health and maintenance-intelligence system for RICE & SHINE, a fictional maker of agricultural machinery with five plants.

## MACHINEX

1. **The person:** the maintenance manager of RICE & SHINE, who is responsible for the machines in all five plants.
2. **The problem:** today maintenance is planned by the calendar: every machine is serviced on fixed dates, whether it needs it or not. The data should change one decision: which machines to service first, based on their actual condition instead of the date.
3. **The first query:** which machines, across the five plants, have shown the most warning signs (alarms and abnormal readings) since their last maintenance, and therefore need attention first?
4. **The data source:** RICE & SHINE is fictional, so there is no real data. We will generate sensor readings and maintenance history for the five plants with a Python script that uses a fixed random seed, the same way as the telemetry generator in [Module 1](../module-01/README.md#4-embedded-vs-clientserver--with-a-measurement), so that anyone can rebuild exactly the same database.
