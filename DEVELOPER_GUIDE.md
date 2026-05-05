# Developer Guide — Smart Bet Field Guide System 2026

> **For contributors, maintainers, and anyone who wants to extend the platform.**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Getting Started (Development)](#getting-started-development)
3. [Database Layer](#database-layer)
4. [Data Ingestion Pipeline](#data-ingestion-pipeline)
5. [Adding New Data Sources](#adding-new-data-sources)
6. [Reports Module](#reports-module)
7. [Betting Utilities](#betting-utilities)
8. [TUI Development](#tui-development)
9. [CLI Development](#cli-development)
10. [Testing & Validation](#testing--validation)
11. [Release Checklist](#release-checklist)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        PRESENTATION                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  TUI         │  │  CLI         │  │  Jupyter     │      │
│  │  (Textual)   │  │  (argparse)  │  │  (pandas)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                      BUSINESS LOGIC                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  reports.py  │  │betting_utils │  │  seed_field  │      │
│  │  (queries)   │  │  (odds, EV)  │  │  _guide.py   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                        DATA LAYER                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLite (fifa2026_repo.db)               │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │    │
│  │  │ players │ │ matches │ │ events  │ │  venues  │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │    │
│  │  │  tiers  │ │ penalty │ │scenarios│ │glossary  │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Historical   │  │ Field Guide  │  │  Future:     │      │
│  │ Open Data    │  │  Reference   │  │  Odds API,   │      │
│  │  (2022 WC)   │  │   (manual)   │  │  Weather,    │      │
│  │              │  │              │  │  Transferm.  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Local-first:** Everything runs on your machine. No API keys required for the core dataset.
2. **Modular:** Each module has a single responsibility. Swap out the ingestion module for a different data source without touching the UI.
3. **SQLite:** Zero-config database. No Docker, no Postgres, no cloud required.
4. **Extensible:** New reports, new tables, and new data sources plug in cleanly.

---

## Getting Started (Development)

### Prerequisites

- Python 3.10 or higher
- `make` (optional, for Makefile convenience)
- `uv` or `pip` for package management

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/sbfg2026.git
cd sbfg2026

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with all extras
pip install -e ".[analytics,notebook,dev]"

# Seed reference data
python src/seed_field_guide.py

# Run tests
make test
```

### Project Layout Conventions

```
src/
  database.py            # Schema + connection (no business logic)
  ingest_<source>.py     # One file per external data source
  seed_<domain>.py       # One file per reference data domain
  reports.py             # All SQL queries return pandas DataFrames
  betting_utils.py       # Pure functions, no side effects
  cli.py                 # argparse commands call reports + utils
  i18n.py                # Bilingual string translations (EN/ES)
  tui_app.py             # Textual screens compose reports + utils
```

---

## Database Layer

### Adding a New Table

1. Add the `CREATE TABLE` statement to `database.py` in `SCHEMA_SQL`.
2. Run `python src/database.py` to apply the schema.
3. Add seed data in a `seed_*.py` script.
4. Add a report function in `reports.py`.
5. Wire it into the CLI (`cli.py`) and TUI (`tui_app.py`).

### Example: Adding a `weather_history` table

```python
# In database.py, add to SCHEMA_SQL:
"""
CREATE TABLE IF NOT EXISTS weather_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_id INTEGER,
    match_date TEXT,
    temperature_c REAL,
    humidity_pct REAL,
    precipitation_mm REAL,
    wind_speed_kmh REAL,
    FOREIGN KEY (venue_id) REFERENCES venues_2026(venue_id)
);
CREATE INDEX IF NOT EXISTS idx_weather_venue ON weather_history(venue_id);
CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_history(match_date);
"""

# Seed script: src/seed_weather.py
from database import execute_many

def seed_weather(db_path=None):
    records = [
        # (venue_id, match_date, temperature_c, humidity_pct, ...)
    ]
    query = "INSERT INTO weather_history (...) VALUES (?, ?, ?, ?, ?, ?)"
    execute_many(query, records, db_path)

# Report function: in reports.py
def report_weather_by_venue(db_path=None):
    query = "SELECT * FROM weather_history JOIN venues_2026 USING (venue_id)"
    return _df_from_query(query, db_path=db_path)
```

### Connection Management

Always use the context manager:

```python
from database import get_connection

with get_connection() as conn:
    rows = conn.execute("SELECT * FROM players WHERE goals > 5").fetchall()
    for row in rows:
        print(dict(row))
```

The context manager automatically handles:
- `sqlite3.Row` factory (dict-like access)
- Connection cleanup

---

## Data Ingestion Pipeline

### Adding a New Data Source

Create `src/ingest_<source>.py` following this pattern:

```python
"""Ingest data from <Source Name>."""

from database import execute_many, get_connection

SOURCE_ID = "my_source"

def ingest_my_source(db_path=None):
    print(f"[1/1] Ingesting from {SOURCE_ID}...")
    # Fetch data
    records = []
    # ... transform ...
    query = "INSERT OR REPLACE INTO my_table (...) VALUES (?, ?)"
    execute_many(query, records, db_path)
    print(f"  -> {len(records)} records ingested")

def run_full_ingestion(db_path=None):
    from database import init_database
    db = init_database(db_path)
    ingest_my_source(db)
    return db

if __name__ == "__main__":
    run_full_ingestion()
```

---

## Reports Module

### Convention

Every report function:
1. Returns a `pandas.DataFrame`
2. Uses `_df_from_query()` for SQL → DataFrame conversion
3. Accepts an optional `db_path` parameter
4. Has a descriptive name: `report_<what>_<filter>()`

### Example Report

```python
def report_players_by_cards(min_cards: int = 2, db_path: str = None) -> pd.DataFrame:
    query = """
        SELECT player_name, team_name, yellow_cards, red_cards, cards_per_90
        FROM players
        WHERE (yellow_cards + red_cards) >= ?
        ORDER BY cards_per_90 DESC
    """
    return _df_from_query(query, (min_cards,), db_path)
```

### Adding a Report to the TUI

1. Create the report function in `reports.py`.
2. Add a `ReportScreen` push in `tui_app.py`:

```python
def action_show_my_report(self) -> None:
    self.app.push_screen(ReportScreen("My Report", report_players_by_cards(3)))
```

3. Add a key binding in `MainScreen.BINDINGS`:

```python
Binding("m", "show_my_report", "My Report"),
```

4. Add a menu item in `MainScreen.compose()`:

```python
yield Static("[b]m[/b]  My Report", classes="menu-item")
```

---

## Betting Utilities

All betting utilities are **pure functions** (no database access, no side effects). This makes them testable and reusable across CLI, TUI, and notebooks.

### Odds Conversion

```python
from betting_utils import parse_odds

odds = parse_odds("+150")
print(odds.decimal)        # 2.500
print(odds.american)       # 150
print(odds.implied_prob)   # 0.400
```

### Kelly Criterion

```python
from betting_utils import kelly_criterion

stake_pct, recommendation = kelly_criterion(
    model_prob=0.45,      # Your estimated probability
    odds_decimal=2.20,    # Decimal odds offered
    fraction=0.25         # Quarter Kelly (conservative)
)
# Returns: (0.0156, "Weak edge—bet 1.56% of bankroll or pass")
```

### Adding a New Calculator

1. Add the function to `betting_utils.py`.
2. Add CLI command in `cli.py`:

```python
def cmd_my_calc(args):
    result = my_calculation(args.param1, args.param2)
    print(f"Result: {result}")

# In main():
p_calc = subparsers.add_parser("mycalc", help="My new calculator")
p_calc.add_argument("--param1", type=float, required=True)
p_calc.set_defaults(func=cmd_my_calc)
```

---

## TUI Development

### Textual Framework

The TUI uses [Textual](https://textual.textualize.io/), a modern Python framework for terminal apps.

### Internationalization

All UI strings live in `src/i18n.py`. To add a new language:

1. Add a new top-level key to `_TRANSLATIONS` (e.g., `"fr"`).
2. Add column mappings to `_COLUMN_MAP`.
3. Launch with `python src/tui_app.py --lang fr`.

### Screen Types

| Screen | Use For |
|:---|:---|
| `ReportScreen` | Any pandas DataFrame |
| `PlayerDetailScreen` | Full player profile (Markdown-rendered) |
| `SearchScreen` | Input + results table |
| `VenueScreen` | Venue data table |
| `MarkdownReportScreen` | Static Markdown content |

### CSS Styling

Textual uses its own CSS-like syntax. The app-level CSS is in `SBFG2026TUI.CSS`:

```python
CSS = """
Screen { align: center middle; }
.report-header { height: 1; background: $primary-darken-2; ... }
DataTable { height: 1fr; border: solid $primary; }
"""
```

For screen-specific styles, use the `CSS` class attribute on the screen class.

### Running the TUI in Dev Mode

Textual has a built-in developer console:

```bash
textual run --dev src/tui_app.py
```

This opens a separate console window with DOM inspector and CSS hot-reload.

---

## CLI Development

### Adding a New Command

1. Write the handler function:

```python
def cmd_my_command(args):
    df = report_my_report(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
```

2. Register the subparser:

```python
p = subparsers.add_parser("mycommand", help="Description")
p.add_argument("--limit", type=int, default=20)
p.set_defaults(func=cmd_my_command)
```

3. Test:

```bash
.venv/bin/python src/cli.py mycommand --limit 10
```

---

## Testing & Validation

### Manual Validation

```bash
make test          # Basic import + count validation
make build-db      # Full pipeline test
python src/cli.py counts   # Verify all tables populated
```

### Data Quality Checks

Run these queries after any ingestion:

```sql
-- Players with minutes but no goals (should be many)
SELECT COUNT(*) FROM players WHERE minutes_played > 0;

-- Players with xG but no goals (under-performers)
SELECT player_name, goals, xg FROM players WHERE xg > 2 AND goals = 0;

-- Matches with no events (should be 0)
SELECT COUNT(*) FROM matches m WHERE NOT EXISTS (
    SELECT 1 FROM match_events e WHERE e.match_id = m.match_id
);
```

---

## Release Checklist

Before pushing to git or releasing:

- [ ] `make test` passes
- [ ] `make build-db` completes without errors
- [ ] `make reports` generates all 16 CSV files
- [ ] `./tui.sh` and `./tui_es.sh` launch and all screens navigate correctly
- [ ] `src/cli.py counts` shows expected row counts
- [ ] README is up to date
- [ ] DEVELOPER_GUIDE reflects current architecture
- [ ] `.gitignore` excludes `data/*.db`, `reports/*.csv`, `.venv/`
- [ ] `pyproject.toml` version bumped if applicable
- [ ] No hardcoded paths or API keys in source

---

## Common Issues

### "Database is locked"

SQLite doesn't support concurrent writes. Close the TUI or any other connection before running ingestion.

### TUI looks garbled in terminal

Ensure your terminal supports Unicode and has at least 80×24 characters. For best results, use a modern terminal (iTerm2, Windows Terminal, GNOME Terminal, Alacritty).

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run the release checklist
5. Submit a pull request

For questions, open an issue or reach out to the maintainers.

---

*Last updated: 2026-05-05*
