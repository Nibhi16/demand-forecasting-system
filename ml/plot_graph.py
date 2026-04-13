import pandas as pd
import matplotlib.pyplot as plt

# Load processed data
df = pd.read_csv("data/processed_orders.csv")

# Sort by time
df = df.sort_values("week")

# Plot
plt.figure()
plt.plot(df["week"], df["num_orders"])
plt.xlabel("Week")
plt.ylabel("Demand (Number of Orders)")
plt.title("Demand vs Time")

plt.show()