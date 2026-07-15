import mimetypes
import os
from pathlib import Path
from typing import Any, Dict

import requests
from dotenv import load_dotenv


load_dotenv()


DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"


def get_content_type(audio_path: Path) -> str:
    content_type, _ = mimetypes.guess_type(str(audio_path))

    if content_type:
        return content_type

    suffix = audio_path.suffix.lower()

    if suffix == ".wav":
        return "audio/wav"
    if suffix == ".mp3":
        return "audio/mpeg"
    if suffix == ".m4a":
        return "audio/mp4"

    return "application/octet-stream"


def transcribe_audio_file(audio_file_path: str) -> Dict[str, Any]:
    api_key = os.getenv("DEEPGRAM_API_KEY")

    if not api_key:
        raise ValueError(
            "Missing DEEPGRAM_API_KEY. Add it to your .env file."
        )

    audio_path = Path(audio_file_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": get_content_type(audio_path)
    }

    params = {
        "model": "nova-3",
        "smart_format": "true",
        "punctuate": "true",
        "paragraphs": "true",
        "utterances": "true",
        "diarize_model": "latest"
    }

    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            DEEPGRAM_URL,
            headers=headers,
            params=params,
            data=audio_file,
            timeout=120
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"Deepgram request failed with status {response.status_code}: "
            f"{response.text}"
        )

    deepgram_response = response.json()

    transcript = extract_transcript(deepgram_response)
    confidence = extract_confidence(deepgram_response)

    return {
        "audio_file": str(audio_path),
        "transcript": transcript,
        "confidence": confidence,
        "raw_response": deepgram_response
    }


def extract_transcript(deepgram_response: Dict[str, Any]) -> str:
    try:
        return deepgram_response["results"]["channels"][0]["alternatives"][0]["transcript"]
    except (KeyError, IndexError):
        return ""


def extract_confidence(deepgram_response: Dict[str, Any]):
    try:
        return deepgram_response["results"]["channels"][0]["alternatives"][0]["confidence"]
    except (KeyError, IndexError):
        return None
