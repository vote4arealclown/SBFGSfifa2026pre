#!/bin/bash
# FIFA 2026 Data Repository - TUI Launcher (Japanese)
# Interactive terminal interface for exploring the dataset

cd "$(dirname "$0")"
./.venv/bin/python src/tui_app.py --lang ja "$@"
