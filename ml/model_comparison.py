import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor


print("🚀 Script started")

# -------------------------------
# LOAD DATA
# -------------------------------
df = pd.read_csv("data/processed_orders.csv")

# Sample for faster training
df = df.sample(n=50000, random_state=42)

print("✅ Data loaded:", df.shape)

# -------------------------------
# FEATURES & TARGET
# -------------------------------
X = df.drop(columns=["num_orders"])
y = df["num_orders"]

# -------------------------------
# TRAIN TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# RANDOM FOREST
# -------------------------------
print("🌳 Training Random Forest...")

rf = RandomForestRegressor(n_estimators=20, random_state=42)
rf.fit(X_train, y_train)

rf_preds = rf.predict(X_test)

rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
rf_mae = mean_absolute_error(y_test, rf_preds)

# -------------------------------
# XGBOOST
# -------------------------------
print("⚡ Training XGBoost...")

xgb = XGBRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42
)

xgb.fit(X_train, y_train)

xgb_preds = xgb.predict(X_test)

xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
xgb_mae = mean_absolute_error(y_test, xgb_preds)

# -------------------------------
# RESULTS
# -------------------------------
print("\n📊 MODEL COMPARISON RESULTS\n")

print("Random Forest:")
print(f"RMSE: {rf_rmse:.2f}")
print(f"MAE : {rf_mae:.2f}")

print("\nXGBoost:")
print(f"RMSE: {xgb_rmse:.2f}")
print(f"MAE : {xgb_mae:.2f}")

# -------------------------------
# FEATURE IMPORTANCE (TOP 10)
# -------------------------------
print("\n📊 Generating Feature Importance...\n")

feature_importance = rf.feature_importances_
features = X.columns

importance_df = pd.DataFrame({
    "feature": features,
    "importance": feature_importance
}).sort_values(by="importance", ascending=False)

top_features = importance_df.head(10)

plt.figure(figsize=(8, 5))
plt.barh(top_features["feature"], top_features["importance"])
plt.gca().invert_yaxis()
plt.title("Top 10 Feature Importance (Random Forest)")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()
# -------------------------------
# SAVE BEST MODEL (XGBOOST)
# -------------------------------
joblib.dump(xgb, "ml/best_model.pkl")
print("✅ Best model (XGBoost) saved successfully!")