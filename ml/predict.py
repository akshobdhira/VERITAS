import joblib
import pandas as pd
import sys

# Load model
model = joblib.load(r"E:\design project\veritas-mvp\ml\model.pkl")

# Load feature CSV (single row)
if len(sys.argv) < 2:
    print("Usage: python predict.py <path_to_features_csv>")
    sys.exit(1)

file_path = sys.argv[1]
df = pd.read_csv(file_path)

# Drop non-numeric columns if they exist (same as in train_model.py)
drop_cols = ["path", "filename", "sha256"]
for col in drop_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# Drop label if exists
if "label" in df.columns:
    df = df.drop(columns=["label"])

prediction = model.predict(df)
confidence = model.predict_proba(df).max()

print("Prediction:", "Malware" if prediction[0] == 1 else "Benign")
print("Confidence:", round(confidence * 100, 2), "%")