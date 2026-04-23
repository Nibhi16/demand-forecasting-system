import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Load processed data
df = pd.read_csv("data/processed_orders.csv")

# Features & target
X = df.drop("num_orders", axis=1)
y = df["num_orders"]

# Train model
model = RandomForestRegressor(n_estimators=50)
model.fit(X, y)

# Save model
joblib.dump(model, "ml/best_model.pkl")

print("✅ Model trained successfully!")