import os
import sys
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, render_template
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.langgraph_workflow import run_finguard_workflow
from src.deepgram_client import transcribe_audio_file


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "FinGuard AI"
    })


@app.route("/analyze", methods=["POST"])
def analyze_transcript():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Missing JSON body."
        }), 400

    transcript = data.get("transcript")

    if not transcript or transcript.strip() == "":
        return jsonify({
            "error": "Missing transcript. Please provide a transcript field."
        }), 400

    try:
        result = run_finguard_workflow(transcript)

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@app.route("/analyze-audio", methods=["POST"])
def analyze_audio():
    if "audio" not in request.files:
        return jsonify({
            "error": "Missing audio file. Upload a file using the field name 'audio'."
        }), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({
            "error": "No selected audio file."
        }), 400

    suffix = Path(audio_file.filename).suffix

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            audio_file.save(temp_file.name)
            temp_audio_path = temp_file.name

        transcription_result = transcribe_audio_file(temp_audio_path)
        transcript = transcription_result["transcript"]

        analysis_result = run_finguard_workflow(transcript)

        return jsonify({
            "success": True,
            "transcript": transcript,
            "deepgram_confidence": transcription_result["confidence"],
            "result": analysis_result
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        if "temp_audio_path" in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


if __name__ == "__main__":
    app.run(debug=True)
