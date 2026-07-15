from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, START, END

from src.risk_model import predict_risk
from src.rag_retriever import (
    retrieve_relevant_policy,
    extract_policy_name,
    extract_recommended_action
)


class FinGuardState(TypedDict, total=False):
    transcript: str
    risk_result: Dict[str, Any]
    retrieved_policy: Dict[str, Any]
    policy_name: str
    recommended_action: str
    final_response: Dict[str, Any]


def classify_risk_node(state: FinGuardState) -> FinGuardState:
    transcript = state["transcript"]

    risk_result = predict_risk(transcript)

    return {
        "risk_result": risk_result
    }


def retrieve_policy_node(state: FinGuardState) -> FinGuardState:
    transcript = state["transcript"]
    risk_result = state["risk_result"]

    rag_query = f"""
    Transcript:
    {transcript}

    Final Risk Prediction:
    {risk_result["final_prediction"]}

    Manual Features:
    {risk_result["manual_features"]}
    """

    retrieved_policies = retrieve_relevant_policy(rag_query, top_k=1)
    best_policy = retrieved_policies[0]

    policy_name = extract_policy_name(best_policy["text"])
    recommended_action = extract_recommended_action(best_policy["text"])

    return {
        "retrieved_policy": best_policy,
        "policy_name": policy_name,
        "recommended_action": recommended_action
    }


def build_final_response_node(state: FinGuardState) -> FinGuardState:
    risk_result = state["risk_result"]
    retrieved_policy = state["retrieved_policy"]

    final_response = {
        "ml_prediction": risk_result["ml_prediction"],
        "final_prediction": risk_result["final_prediction"],
        "decision_reason": risk_result["decision_reason"],
        "probabilities": risk_result["probabilities"],
        "manual_features": risk_result["manual_features"],
        "retrieved_policy": state["policy_name"],
        "policy_file": retrieved_policy["file_name"],
        "policy_similarity_score": retrieved_policy["similarity_score"],
        "recommended_action": state["recommended_action"]
    }

    return {
        "final_response": final_response
    }


def build_finguard_graph():
    workflow = StateGraph(FinGuardState)

    workflow.add_node("classify_risk", classify_risk_node)
    workflow.add_node("retrieve_policy", retrieve_policy_node)
    workflow.add_node("build_final_response", build_final_response_node)

    workflow.add_edge(START, "classify_risk")
    workflow.add_edge("classify_risk", "retrieve_policy")
    workflow.add_edge("retrieve_policy", "build_final_response")
    workflow.add_edge("build_final_response", END)

    graph = workflow.compile()

    return graph


def run_finguard_workflow(transcript: str):
    graph = build_finguard_graph()

    result = graph.invoke({
        "transcript": transcript
    })

    return result["final_response"]
