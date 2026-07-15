from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]
POLICY_DIR = BASE_DIR / "data" / "policies"


def load_policy_documents():
    policy_documents = []

    for file_path in POLICY_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        policy_documents.append({
            "file_name": file_path.name,
            "text": text
        })

    if not policy_documents:
        raise FileNotFoundError(
            f"No policy documents found in {POLICY_DIR}. "
            "Create policy .txt files first."
        )

    return policy_documents


def retrieve_relevant_policy(query, top_k=1):
    policy_documents = load_policy_documents()

    policy_texts = [doc["text"] for doc in policy_documents]

    vectorizer = TfidfVectorizer(stop_words="english")
    document_vectors = vectorizer.fit_transform(policy_texts)

    query_vector = vectorizer.transform([query])

    similarity_scores = cosine_similarity(query_vector, document_vectors)[0]

    ranked_indexes = similarity_scores.argsort()[::-1][:top_k]

    results = []

    for index in ranked_indexes:
        policy_doc = policy_documents[index]

        results.append({
            "file_name": policy_doc["file_name"],
            "similarity_score": round(float(similarity_scores[index]), 4),
            "text": policy_doc["text"]
        })

    return results


def extract_policy_name(policy_text):
    lines = policy_text.splitlines()

    for line in lines:
        if line.lower().startswith("policy name:"):
            return line.replace("Policy Name:", "").strip()

    return "Unknown Policy"


def extract_recommended_action(policy_text):
    lines = policy_text.splitlines()

    for line in lines:
        if line.lower().startswith("recommended action:"):
            return line.replace("Recommended Action:", "").strip()

    return "No recommended action found."
