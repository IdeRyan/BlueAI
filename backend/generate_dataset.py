import csv
import os
import random

# Configuration
SEED = 42
OUTPUT_DIR = "./data"

N_TRAINING = 5000
N_SIM = 5000


NORMAL_FLOW_MIN = 2.4
NORMAL_FLOW_MAX = 2.6
NORMAL_LOSS_MIN = 0.0
NORMAL_LOSS_MAX = 0.05
NORMAL_NOISE = 0.02    

LEAK_RATIO_MIN = 0.55
LEAK_RATIO_MAX = 0.80
LEAK_NOISE = 0.15           

OFF_FLOW_MIN = 0.0
OFF_FLOW_MAX = 0.05
OFF_NOISE = 0.01


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def write_csv(filename, rows):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["flow1", "flow2", "label"])
        writer.writerows(rows)


def generate_normal(n):
    rows = []
    for _ in range(n):
        flow1 = round(random.uniform(NORMAL_FLOW_MIN, NORMAL_FLOW_MAX), 3)
        loss = random.uniform(NORMAL_LOSS_MIN, NORMAL_LOSS_MAX)
        flow2_base = flow1 - loss
        noise = random.uniform(-NORMAL_NOISE, NORMAL_NOISE)
        flow2 = round(flow2_base + noise, 3)
        rows.append((flow1, flow2, 0))
    return rows


def generate_leak(n):
    rows = []
    for _ in range(n):
        flow1 = round(random.uniform(NORMAL_FLOW_MIN, NORMAL_FLOW_MAX), 3)
        ratio = random.uniform(LEAK_RATIO_MIN, LEAK_RATIO_MAX)
        flow2_base = flow1 * ratio
        noise = random.uniform(-LEAK_NOISE, LEAK_NOISE)
        flow2 = round(flow2_base + noise, 3)
        rows.append((flow1, flow2, 1))
    return rows


def generate_off(n):
    rows = []
    for _ in range(n):
        flow1 = round(random.uniform(OFF_FLOW_MIN, OFF_FLOW_MAX), 3)
        flow2 = round(random.uniform(OFF_FLOW_MIN, OFF_FLOW_MAX), 3)
        rows.append((flow1, flow2, 0))
    return rows

def main():
    random.seed(SEED)
    ensure_output_dir()

    print("\n📊 Génération des datasets synthétiques BlueAI")
    print(f"   Seed : {SEED}")
    print()

    # Dataset to train the model
    print("🎓 Dataset d'entraînement :")
    train_normal = generate_normal(N_TRAINING)
    train_leak = generate_leak(N_TRAINING)

    training_rows = train_normal + train_leak
    random.shuffle(training_rows)
    write_csv("training_dataset.csv", training_rows)

    # Dataset simulations
    print("\n🎮 Datasets de simulation :")
    sim_normal = generate_normal(N_SIM)
    sim_leak = generate_leak(N_SIM)
    sim_off = generate_off(N_SIM)

    write_csv("sim_normal.csv", sim_normal)
    write_csv("sim_leak.csv", sim_leak)
    write_csv("sim_off.csv", sim_off)


    print(f"   - training_dataset.csv : {len(training_rows)} lignes (Normal + Leak)")
    print(f"   - sim_normal.csv : {len(sim_normal)} lignes (label 0)")
    print(f"   - sim_leak.csv   : {len(sim_leak)} lignes (label 1)")
    print(f"   - sim_off.csv    : {len(sim_off)} lignes (label 0)")
    print()


if __name__ == "__main__":
    main()