def row_to_dict(row:tuple) -> dict:
    result = {
        "id": row[0],
        "measurement_id": row[1],
        "label": row[2],
        "confidence": row[3],
        "flow1_avg": row[4],
        "flow2_avg": row[5],
        "flow_diff": row[6],
        "flow_ratio": row[7],
        "flow2_var": row[8],
        "timestamp": row[9],
        "flow1": row[10],
        "flow2": row[11]
    }

    return result