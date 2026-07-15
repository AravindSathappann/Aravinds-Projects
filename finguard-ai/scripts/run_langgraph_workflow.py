import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.langgraph_workflow import run_finguard_workflow


def main():
    transcript = """
    Customer: I did not authorize this 950 dollar transaction.
    Customer: My card may have been stolen and I need this fixed today.
    Agent: I can help you open a dispute case.
    Customer: I am very frustrated because I already called twice.
    """

    result = run_finguard_workflow(transcript)

    print("LangGraph FinGuard AI Result")
    print("=" * 40)

    print("\nML Prediction:")
    print(result["ml_prediction"])

    print("\nFinal Prediction:")
    print(result["final_prediction"])

    print("\nDecision Reason:")
    print(result["decision_reason"])

    print("\nRetrieved Policy:")
    print(result["retrieved_policy"])

    print("\nPolicy File:")
    print(result["policy_file"])

    print("\nPolicy Similarity Score:")
    print(result["policy_similarity_score"])

    print("\nRecommended Action:")
    print(result["recommended_action"])

    print("\nManual Features:")
    for feature_name, feature_value in result["manual_features"].items():
        print(feature_name, feature_value)


if __name__ == "__main__":
    main()
