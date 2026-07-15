import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.deepgram_client import transcribe_audio_file
from src.langgraph_workflow import run_finguard_workflow


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe a financial call with Deepgram and analyze it with FinGuard AI."
    )

    parser.add_argument(
        "--audio",
        required=True,
        help="Path to local audio file, such as data/sample_audio/fraud_call.wav"
    )

    args = parser.parse_args()

    transcription_result = transcribe_audio_file(args.audio)
    transcript = transcription_result["transcript"]

    print("Deepgram Transcript")
    print("=" * 40)
    print(transcript)

    print("\nDeepgram Confidence")
    print("=" * 40)
    print(transcription_result["confidence"])

    analysis_result = run_finguard_workflow(transcript)

    print("\nFinGuard AI Analysis")
    print("=" * 40)

    print("\nML Prediction:")
    print(analysis_result["ml_prediction"])

    print("\nFinal Prediction:")
    print(analysis_result["final_prediction"])

    print("\nDecision Reason:")
    print(analysis_result["decision_reason"])

    print("\nRetrieved Policy:")
    print(analysis_result["retrieved_policy"])

    print("\nRecommended Action:")
    print(analysis_result["recommended_action"])

    print("\nManual Features:")
    for feature_name, feature_value in analysis_result["manual_features"].items():
        print(feature_name, feature_value)


if __name__ == "__main__":
    main()
