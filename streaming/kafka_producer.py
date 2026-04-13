import pandas as pd
import json
import time
from kafka import KafkaProducer

# Load data
df = pd.read_csv("data/processed_orders.csv")

# Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = "food-demand"

print("🚀 Kafka Producer started...")

for _, row in df.iterrows():
    data = {
        "week": int(row["week"]),
        "center_id": int(row["center_id"]),
        "meal_id": int(row["meal_id"]),
        "lag_1": float(row["lag_1"]),
        "lag_2": float(row["lag_2"])
    }

    producer.send(topic, value=data)
    print(f"Sent: {data}")

    time.sleep(1)