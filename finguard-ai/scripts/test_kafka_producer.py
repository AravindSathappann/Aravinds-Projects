import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from kafka.producer import publish_call_risk_event


def main():
    fake_result = {
        "ml_prediction": "Fraud Risk",
        "final_prediction": "Fraud Risk",
        "decision_reason": "Test fraud event.",
        "retrieved_policy": "Unauthorized Transaction Dispute Policy",
        "policy_file": "fraud_dispute_policy.txt",
        "policy_similarity_score": 0.6019,
        "recommended_action": "Route to fraud specialist and open a dispute case.",
        "manual_features": {
            "dollar_amount_count": 1,
            "fraud_keyword_count": 3,
            "risk_keyword_total": 4
        }
    }

    event = publish_call_risk_event(
        result=fake_result,
        transcript="Customer did not authorize this 950 dollar transaction."
    )

    print("Published event:")
    print(event)


if __name__ == "__main__":
    main()
