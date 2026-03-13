import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Load dataset
df = pd.read_csv(r"E:\design project\veritas-mvp\dataset\fused_features.csv")

# Drop non-numeric columns if they exist
drop_cols = ["path", "filename", "sha256"]
for col in drop_cols:
    if col in df.columns:
        df = df.drop(columns=[col])

# Drop any rows with NaN values to prevent modeling errors
df = df.dropna()

# Separate features and label
X = df.drop(columns=["label"])
y = df["label"]

if len(df) <= 1:
    print("Dataset too small to split! Training on the entire dataset without evaluation.")
    X_train, y_train = X, y
    X_test, y_test = X.copy(), y.copy()
else:
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

if len(df) > 1:
    # Evaluate
    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

# Save model (create directory if it doesn't exist)
import os
os.makedirs("ml", exist_ok=True)
joblib.dump(model, r"E:\design project\veritas-mvp\ml\model.pkl")

print("Model saved as model.pkl")