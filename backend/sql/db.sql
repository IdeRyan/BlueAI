CREATE TABLE IF NOT EXISTS measurements(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow1 REAL NOT NULL,
    flow2 REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL,
    label INTEGER NOT NULL,
    confidence REAL NOT NULL,
    flow1_avg REAL NOT NULL,
    flow2_avg REAL NOT NULL,
    flow_diff REAL NOT NULL,
    flow_ratio REAL NOT NULL,
    flow2_var REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (measurement_id) REFERENCES measurements(id)
);

CREATE INDEX IF NOT EXISTS measurements_id_index ON measurements(id);
CREATE INDEX IF NOT EXISTS predictions_id_index ON predictions(id);