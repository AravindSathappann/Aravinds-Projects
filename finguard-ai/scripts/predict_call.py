import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.risk_model import predict_risk
from src.rag_retriever import (
    retrieve_relevant_policy,
    extract_policy_name,
    extract_recommended_action
)


def main():
    transcript = """
    Customer: I did not authorize this 950 dollar transaction.
    Customer: My card may have been stolen and I need this fixed today.
    Agent: I can help you open a dispute case.
    Customer: I am very frustrated because I already called twice.
    """

    result = predict_risk(transcript)

    rag_query = f"""
    Transcript:
    {transcript}

    Final Risk Prediction:
    {result["final_prediction"]}

    Manual Features:
    {result["manual_features"]}
    """

    retrieved_policies = retrieve_relevant_policy(rag_query, top_k=1)
    best_policy = retrieved_policies[0]

    policy_name = extract_policy_name(best_policy["text"])
    recommended_action = extract_recommended_action(best_policy["text"])

    print("Transcript:")
    print(transcript)

    print("\nML Prediction:")
    print(result["ml_prediction"])

    print("\nFinal Prediction:")
    print(result["final_prediction"])

    print("\nDecision Reason:")
    print(result["decision_reason"])

    print("\nProbabilities:")
    for label, probability in result["probabilities"].items():
        print(label, probability)

    print("\nManual Features:")
    for feature_name, feature_value in result["manual_features"].items():
        print(feature_name, feature_value)

    print("\nRetrieved Policy:")
    print(policy_name)

    print("\nPolicy File:")
    print(best_policy["file_name"])

    print("\nPolicy Similarity Score:")
    print(best_policy["similarity_score"])

    print("\nRecommended Action:")
    print(recommended_action)


if __name__ == "__main__":
    main()
