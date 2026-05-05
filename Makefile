.PHONY: help install build-all reports tui cli clean test

PYTHON := .venv/bin/python
PIP := .venv/bin/pip

help:
	@echo "Smart Bet Field Guide System 2026 — Makefile"
	@echo ""
	@echo "  make install      Create venv and install dependencies"
	@echo "  make build-all    Full build: install + reports"
	@echo "  make reports      Generate all CSV reports"
	@echo "  make tui          Launch the interactive terminal UI"
	@echo "  make cli          Launch the command-line interface"
	@echo "  make clean        Remove generated files and database"
	@echo "  make test         Run basic validation tests"

install:
	@echo "Creating virtual environment..."
	@python3 -m venv .venv || true
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "Installation complete. Run 'make reports' next."

build-all: install reports
	@echo "Full build complete."

reports:
	@echo "Generating CSV reports..."
	@$(PYTHON) -c "import sys; sys.path.insert(0, 'src'); from reports import export_all_reports; export_all_reports()"
	@echo "Reports saved to reports/"

tui:
	@$(PYTHON) src/tui_app.py

cli:
	@$(PYTHON) src/cli.py

clean:
	@rm -f data/fifa2026_repo.db
	@rm -f reports/*.csv
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned generated files."

test:
	@$(PYTHON) -c "import sys; sys.path.insert(0, 'src'); from database import table_counts; print(table_counts())"
	@echo "Basic import test passed."
