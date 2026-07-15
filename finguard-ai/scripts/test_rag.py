import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.rag_retriever import (
    retrieve_relevant_policy,
    extract_policy_name,
    extract_recommended_action
)


def main():
    transcript = """
    Customer: I did not authorize this 950 dollar transaction.
    Customer: My card may have been stolen.
    Customer: I need to dispute this charge immediately.
    """

    retrieved_policies = retrieve_relevant_policy(transcript, top_k=1)

    best_policy = retrieved_policies[0]

    policy_name = extract_policy_name(best_policy["text"])
    recommended_action = extract_recommended_action(best_policy["text"])

    print("Best Policy Match:")
    print(policy_name)

    print("\nPolicy File:")
    print(best_policy["file_name"])

    print("\nSimilarity Score:")
    print(best_policy["similarity_score"])

    print("\nRecommended Action:")
    print(recommended_action)


if __name__ == "__main__":
    main()
