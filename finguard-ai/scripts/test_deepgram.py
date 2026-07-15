import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.deepgram_client import transcribe_audio_file


def main():
    audio_path = "data/sample_audio/fraud_call.mp3"

    result = transcribe_audio_file(audio_path)

    print("Audio File:")
    print(result["audio_file"])

    print("\nTranscript:")
    print(result["transcript"])

    print("\nConfidence:")
    print(result["confidence"])


if __name__ == "__main__":
    main()
