import sqlite3

connection = sqlite3.connect("./database/blue_ai.db")

def init_db():
    with open("./sql/db.sql") as f:
        content = f.read()
        connection.executescript(content)
        connection.commit()

def insert_measurement(flow_1, flow_2):
    sql = """
        INSERT INTO measurements(flow1, flow2) VALUES(?, ?);
    """
    cursor = connection.execute(sql, [flow_1, flow_2])
    connection.commit()
    return cursor.lastrowid
    
def insert_prediction(measurement_id, label, confidence, flow1_avg, flow2_avg, flow_diff, flow_ratio, flow2_var):
    sql ="""
        INSERT INTO predictions
            (measurement_id, label, confidence, flow1_avg, flow2_avg, flow_diff, flow_ratio, flow2_var)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?);
    """
    connection.execute(sql,[measurement_id, label, confidence, flow1_avg, flow2_avg, flow_diff, flow_ratio, flow2_var])
    connection.commit()

def get_5_last_measurements():
    sql = """
        SELECT * FROM measurements ORDER BY id DESC LIMIT 5;
    """
    cursor = connection.execute(sql)
    return cursor.fetchall()

def get_latest_prediction():
    sql = """
        SELECT p.*, m.flow1, m.flow2
        FROM predictions p
        JOIN measurements m ON m.id = p.measurement_id
        ORDER BY p.id DESC
        LIMIT 1;
    """
    cursor = connection.execute(sql)
    return cursor.fetchone()

def get_history(n):
    sql = """
        SELECT * FROM (
        SELECT p.id AS pred_id p.*, m.flow1, m.flow2
        FROM predictions p
        JOIN measurements m ON m.id = p.measurement_id
        ORDER BY p.id DESC
        LIMIT ?
        ) ORDER BY pred_id ASC;
    """
    cursor = connection.execute(sql, (n,))
    return cursor.fetchall()
