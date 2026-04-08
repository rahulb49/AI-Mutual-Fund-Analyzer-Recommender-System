#!/usr/bin/env python
"""Streamlit Dashboard Launcher"""

import sys
import subprocess
from pathlib import Path

# Get the virtual environment Python executable
venv_path = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"

if venv_path.exists():
    # Run streamlit with venv python
    args = [str(venv_path), "-m", "streamlit", "run", "UI/app.py", "--server.port", "8501"]
    subprocess.run(args)
else:
    # Fallback to system python
    args = [sys.executable, "-m", "streamlit", "run", "UI/app.py", "--server.port", "8501"]
    subprocess.run(args)
