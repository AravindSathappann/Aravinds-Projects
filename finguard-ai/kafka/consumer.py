import json

from confluent_kafka import Consumer


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CALL_RISK_TOPIC = "call_risk_events"


def main():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "finguard-risk-consumer",
        "auto.offset.reset": "earliest"
    })

    consumer.subscribe([CALL_RISK_TOPIC])

    print(f"Listening for events on topic: {CALL_RISK_TOPIC}")
    print("Press Control + C to stop.")

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue

            if message.error():
                print("Consumer error:", message.error())
                continue

            event = json.loads(message.value().decode("utf-8"))

            print("\nReceived Kafka Event")
            print("=" * 40)
            print("Event ID:", event["event_id"])
            print("Final Prediction:", event["final_prediction"])
            print("Retrieved Policy:", event["retrieved_policy"])
            print("Recommended Action:", event["recommended_action"])

    except KeyboardInterrupt:
        print("Stopping consumer.")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()
