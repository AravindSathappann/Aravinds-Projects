#!/bin/bash
cd "$(dirname "$0")" || exit 1
if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
else
  CANDIDATE=""
  for cmd in python3.12 python3.11 python3.13 python3; do
    if command -v "$cmd" >/dev/null 2>&1; then
      ver=$($cmd -c 'import sys;print(1 if (3,10)<=sys.version_info[:2]<(3,14) else 0)' 2>/dev/null)
      if [ "$ver" = 1 ]; then CANDIDATE=$(command -v "$cmd");break;fi
    fi
  done
  if [ -z "$CANDIDATE" ] && command -v brew >/dev/null 2>&1; then
    for formula in python@3.11 python@3.12 python@3.13; do
      prefix=$(brew --prefix "$formula" 2>/dev/null)
      for candidate in "$prefix/bin/python3.11" "$prefix/bin/python3.12" "$prefix/bin/python3.13"; do
        if [ -x "$candidate" ]; then CANDIDATE="$candidate";break;fi
      done
      [ -n "$CANDIDATE" ] && break
      candidate=$(brew list "$formula" 2>/dev/null | grep -E '/bin/python3\.(11|12|13)$' | head -1)
      if [ -x "$candidate" ]; then CANDIDATE="$candidate";break;fi
    done
  fi
  if [ -z "$CANDIDATE" ]; then
    echo 'Python 3.10–3.13 is needed. Try: brew install python@3.11'
    read -r -p 'Press Enter to close...'
    exit 1
  fi
  echo "Using Python: $CANDIDATE"
  "$CANDIDATE" -m venv .venv || exit 1
  PY=.venv/bin/python
fi
"$PY" -m pip install -r requirements.txt || { echo 'Install failed';read -r -p 'Press Enter to close...';exit 1; }
"$PY" -m streamlit run app.py
