import json
import requests
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'food-demand',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("📡 Kafka Consumer started...")

for message in consumer:
    data = message.value

    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=data
        )

        result = response.json()

        print("\n---------------------------------")
        print(f"Week: {data['week']} | Center: {data['center_id']}")
        print(f"Predicted Demand: {result['predicted_demand']}")
        print(f"Decision: {result['allocation_decision']}")
        print("---------------------------------")

    except Exception as e:
        print("Error:", e)