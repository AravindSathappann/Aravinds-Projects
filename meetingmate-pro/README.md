# MeetingMate Pro

Deepgram Nova-3 prerecorded speech transcription + an explainable, evidence-grounded meeting analytics dashboard.

## Easiest setup on Mac

1. Unzip the archive.
2. Open the `meetingmate-pro` folder and double-click `start.command` (right-click > Open if macOS warns).
3. Click **Instant demo** to explore without an API key.
4. For real recordings, enter a key from https://console.deepgram.com/ in the sidebar and upload an audio file or record through your browser.

The launcher creates its own virtual environment and installs only Streamlit and Requests. Python 3.10–3.13 is required. It will try Homebrew Python 3.11 automatically even when it isn't on your PATH.

## Manual start

```bash
cd ~/Downloads/meetingmate-pro
source .venv/bin/activate  # after running start.command once
python -m streamlit run app.py
```

## Features

- Prerecorded audio transcription using Deepgram Nova-3 and diarization
- Browser recording (record, stop, then transcribe; **not live WebSocket streaming**)
- Dashboard for speaker speaking time, keyword trends, actions, decisions, and blockers
- Transcript search using dependency-free TF-IDF cosine similarity and verbatim evidence, rather than hallucinated answers
- Optional **local** SQLite meeting history (opt-in), with delete-history control
- Download transcript, Markdown report, or JSON data
- Free, offline built-in demo (no API calls)

## Important limitations

Deepgram usage may be billed. API key is held in current app input; never publish it. User audio is sent to Deepgram only when you press Analyze. Saved transcripts remain on your computer in `meetingmate_history.db`; deleting all local history removes database rows. Demo is synthetic. Action extraction and decision/risk identification are simple rules, tone is lexicon-based, summaries are extractive, and question answering retrieves passages rather than generating answers. Verify any highlighted claims yourself. No live microphone streaming or LLM/RAG pipeline is claimed.
