import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from features import compute_feature
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib


def build_features(df):
    """
    Calcule les features sur des fenêtres de 5 lignes consécutives.
    Retourne (features_list, labels).
    """
    features_list = []
    labels = []
    for i in range(4, len(df)):
        window = df.iloc[i-4:i+1]
        features = compute_feature(window.values.tolist())
        features_list.append(features)
        labels.append(df['label'].iloc[i])
    return features_list, labels

# mixed label
df = pd.read_csv("./data/training_dataset.csv")

print(f"Dataset total : {len(df)} lignes")
print(f"Distribution des labels :")
print(df["label"].value_counts())
print()

# separate class
df_normal = df[df["label"] == 0].reset_index(drop=True)
df_leak = df[df["label"] == 1].reset_index(drop=True)

print(f"Normal : {len(df_normal)} lignes")
print(f"Leak   : {len(df_leak)} lignes")
print()


features_normal, labels_normal = build_features(df_normal)
features_leak, labels_leak = build_features(df_leak)

print(f"Features Normal : {len(features_normal)}")
print(f"Features Leak   : {len(features_leak)}")
print()

# concatenate features from each class
all_features = features_normal + features_leak
all_labels = labels_normal + labels_leak

# create final DataFrame
new_dataset = pd.DataFrame(all_features, columns=[
    "flow1_avg", "flow2_avg", "flow_diff", "flow_ratio", "flow2_var"
])
new_dataset["label"] = all_labels


new_dataset = new_dataset.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Dataset final : {len(new_dataset)} lignes")
print()


X = new_dataset[["flow1_avg", "flow2_avg", "flow_diff", "flow_ratio", "flow2_var"]]
y = new_dataset["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)

predictions_test = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions_test))
print("\nClassification Report:")
print(classification_report(y_test, predictions_test, target_names=['Normal', 'Leak']))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions_test))


joblib.dump(model, "./models/blue_ai_model.pkl")
print("\n Modèle sauvegardé dans ./models/blue_ai_model.pkl")