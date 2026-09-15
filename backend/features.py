import numpy as np

def compute_feature(last_5:list):
    features = []

    flow1_avg = np.mean([measure[1] for measure in last_5])
    features.append(flow1_avg)

    flow2_avg = np.mean([measure[2] for measure in last_5])
    features.append(flow2_avg)

    # flow_diff
    features.append((flow1_avg - flow2_avg))

    # flow_ratio
    flow_ratio = flow2_avg / flow1_avg if flow1_avg > 0 else 0

    # flow2_var
    features.append(np.var([measure[2] for measure in last_5]))

    return features