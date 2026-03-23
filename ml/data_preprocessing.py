import pandas as pd

# Load datasets
df = pd.read_csv("data/food_demand.csv")
meal = pd.read_csv("data/meal_info.csv")
center = pd.read_csv("data/fulfilment_center_info.csv")

# Merge datasets
df = df.merge(meal, on="meal_id", how="left")
df = df.merge(center, on="center_id", how="left")

# Sort by time
df = df.sort_values(by="week")

# Create lag features
df["lag_1"] = df["num_orders"].shift(1)
df["lag_2"] = df["num_orders"].shift(2)

# Drop missing values
df = df.dropna()

# Select useful features
df = df[[
    "week",
    "center_id",
    "meal_id",
    "category",
    "cuisine",
    "city_code",
    "region_code",
    "center_type",
    "op_area",
    "lag_1",
    "lag_2",
    "num_orders"
]]

# Convert categorical to numeric
df = pd.get_dummies(df, columns=["category", "cuisine", "center_type"])

# Save processed data
df.to_csv("data/processed_orders.csv", index=False)

print("✅ Data merged and processed successfully!")