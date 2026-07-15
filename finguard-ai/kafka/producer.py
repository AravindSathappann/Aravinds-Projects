import json
from datetime import datetime
from uuid import uuid4

from confluent_kafka import Producer


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
CALL_RISK_TOPIC = "call_risk_events"


def create_kafka_producer():
    return Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
    })


def delivery_report(error, message):
    if error is not None:
        print(f"Kafka delivery failed: {error}")
    else:
        print(
            f"Kafka message delivered to {message.topic()} "
            f"[partition {message.partition()}]"
        )


def publish_call_risk_event(result, transcript=None):
    producer = create_kafka_producer()

    event = {
        "event_id": str(uuid4()),
        "event_time": datetime.utcnow().isoformat(),
        "transcript": transcript,
        "ml_prediction": result.get("ml_prediction"),
        "final_prediction": result.get("final_prediction"),
        "decision_reason": result.get("decision_reason"),
        "retrieved_policy": result.get("retrieved_policy"),
        "policy_file": result.get("policy_file"),
        "policy_similarity_score": result.get("policy_similarity_score"),
        "recommended_action": result.get("recommended_action"),
        "manual_features": result.get("manual_features")
    }

    producer.produce(
        CALL_RISK_TOPIC,
        key=event["event_id"],
        value=json.dumps(event),
        callback=delivery_report
    )

    producer.flush()

    return event
