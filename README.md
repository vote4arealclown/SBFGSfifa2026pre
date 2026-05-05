# Smart Bet Field Guide System 2026 (SBFG2026)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **EN:** A comprehensive local data warehouse and betting analytics platform for the 2026 FIFA World Cup.
>
> **ES:** Una plataforma local completa de análisis de apuestas e inteligencia deportiva para la Copa Mundial de la FIFA 2026.
>
> **JA:** 2026年FIFAワールドカップ向けの包括的なローカルデータ倉庫およびベッティング分析プラットフォーム。

Built on the complete **FIFA World Cup 2022** dataset from public open-data repositories, SBFG2026 transforms tournament complexity into actionable intelligence—giving you a structural edge before the market catches up.

```
┌─────────────────────────────────────────────────────────────┐
│  829 Players  •  32 Teams  •  64 Matches  •  ~7,400 Events  │
│  xG Data  •  Team Tiers  •  Penalty Takers  •  Venue Intel  │
│  Kelly Criterion  •  CLV Analysis  •  Live Bet Scenarios    │
└─────────────────────────────────────────────────────────────┘
```

---

## Why This Exists

The 2026 World Cup is the most consequential transformation in tournament history for betting markets:

- **48 teams** (+50% field expansion) — pricing inefficiencies on unfamiliar nations
- **104 matches** (+62.5% volume) — longest sustained betting opportunity ever
- **Round of 32** — no historical World Cup data = temporary market inefficiency
- **16 venues** across Canada, Mexico, US — altitude, humidity, and travel create edges the market ignores

Your edge will not come from knowing Brazil is good. It will come from understanding that the market prices Brazil as "good" while ignoring they are playing their third match in eight days at 2,240 meters elevation against a team that needs only a draw to advance.

---

## Quick Start

### Clone & Build

```bash
git clone https://github.com/yourusername/sbfg2026.git
cd sbfg2026
make install      # Create venv + install dependencies
make reports      # Generate all CSV exports
```

### Launch the Interactive TUI

```bash
./tui.sh       # English (default)
./tui_es.sh    # Spanish
./tui_ja.sh    # Japanese
```

Or pass `--lang` directly:
```bash
.venv/bin/python src/tui_app.py --lang es
.venv/bin/python src/tui_app.py --lang ja
```

| Key | Report | Key | Report |
|:---|:---|:---|:---|
| `1` | Top Scorers | `6` | Team Summary |
| `2` | Top Assisters | `7` | Full Roster |
| `3` | Top xG | `8` | 2026 Venues |
| `4` | Defensive Leaders | `9` | Team Tiers |
| `5` | Goalkeepers | `0` | Penalty Takers |
| `p` | Set-Piece Specs | `b` | Live Bet Scenarios |
| `d` | Key Dates | `e` | Environmental Matrix |
| `l` | Checklist | `r` | Bankroll Framework |
| `g` | Glossary | `s` | Player Search |
| `q` | Quit | `Esc` | Back |

### CLI Examples

```bash
# Player analytics
.venv/bin/python src/cli.py scorers --limit 10
.venv/bin/python src/cli.py xg --limit 10
.venv/bin/python src/cli.py roster --team "Argentina"
.venv/bin/python src/cli.py search "Mbappé"

# Field Guide intelligence
.venv/bin/python src/cli.py tiers
.venv/bin/python src/cli.py penalties
.venv/bin/python src/cli.py scenarios
.venv/bin/python src/cli.py environment
.venv/bin/python src/cli.py bankroll

# Betting utilities
.venv/bin/python src/cli.py odds --value +150
.venv/bin/python src/cli.py kelly --prob 0.42 --odds 2.50
.venv/bin/python src/cli.py clv --entry 2.20 --close 2.00
.venv/bin/python src/cli.py ev --prob 0.45 --odds 2.20
```

---

## What's Inside

### Core Dataset (FIFA 2022 → Foundation for 2026)

| Asset | Count | Description |
|:---|:---|:---|
| Teams | 32 | Nations with group assignments |
| Players | 829 | Full profiles with tournament stats & per-90 rates |
| Matches | 64 | All fixtures with scores, metadata, referees |
| Events | ~7,400 | Shots, goals, cards, substitutions, fouls |
| Player-Match Stats | ~2,000 | Granular per-match aggregations |
| xG Data | All shots | Expected goals model |

### Field Guide Intelligence

| Feature | Records | Use Case |
|:---|:---|:---|
| **Team Tiers** | 11 | Tier 1 Favorites → Tier 3 Host Nations with betting angles |
| **Penalty Takers** | 15 | PK conversion rates for player prop modeling |
| **Set-Piece Specialists** | 10 | Corner/free kick takers for team props |
| **Environmental Matrix** | 5 | Altitude/heat/humidity impact by venue |
| **Live Bet Scenarios** | 6 | Pre-defined situational playbooks |
| **Bankroll Framework** | 5 phases | 40/15/10/10/25 allocation with daily limits |
| **Key Dates** | 10 | Critical milestones with betting actions |
| **Checklist** | 20 items | Pre-tournament preparation tracker |
| **Glossary** | 20 terms | Betting terminology with 2026 relevance |

### Betting Utilities

| Tool | Function |
|:---|:---|
| **Odds Converter** | Decimal ↔ American ↔ Fractional with implied probability |
| **Kelly Criterion** | Bankroll-optimized bet sizing (with fractional Kelly) |
| **CLV Calculator** | Closing Line Value analysis |
| **EV Calculator** | Expected value for any probability/odds pair |

---

## Project Structure

```
sbfg2026/
├── data/
│   └── fifa2026_repo.db          # SQLite database (generated)
├── reports/                      # CSV exports (generated)
├── src/
│   ├── database.py               # Schema & connection manager
│   ├── seed_field_guide.py       # Field Guide reference data
│   ├── reports.py                # Reporting & analytics queries
│   ├── betting_utils.py          # Odds, Kelly, CLV, EV calculators
│   ├── cli.py                    # Command-line interface
│   └── tui_app.py                # Interactive terminal UI (Textual)
├── notebooks/
│   └── 01_exploratory_analysis.ipynb
├── .venv/                        # Python virtual environment
├── .gitignore
├── Makefile
├── pyproject.toml
├── requirements.txt
├── tui.sh                        # TUI launcher (English)
├── tui_es.sh                     # TUI launcher (Spanish)
├── tui_ja.sh                     # TUI launcher (Japanese)
├── README.md                     # This file
├── DEVELOPER_GUIDE.md            # Contributor documentation
├── GUIA_DESARROLLADOR.md         # Guía del desarrollador (español)
└── DEVELOPER_GUIDE_JA.md         # 開発者ガイド (日本語)
```

---

## Database Schema

### Core Tables

| Table | Purpose |
|:---|:---|
| `teams` | 32 national teams |
| `players` | 829 player profiles with aggregated 2022 stats |
| `matches` | 64 match records with scores and metadata |
| `match_events` | Key events (shots, goals, cards, subs, fouls) |
| `player_match_stats` | Per-player per-match granular statistics |
| `match_lineups` | Lineups with minutes played and starter status |
| `venues_2026` | 2026 host stadium environmental profiles |

### Reference Tables

| Table | Purpose |
|:---|:---|
| `team_tiers` | Tier 1-3 classifications with betting angles |
| `penalty_takers` | PK takers with conversion rates and notes |
| `set_piece_specialists` | Corners, free kicks, penalties by player |
| `betting_glossary` | 20 betting terms with 2026 relevance |
| `key_dates` | Tournament milestone timeline |
| `checklist_items` | 20-item pre-tournament preparation tracker |
| `betting_scenarios` | 6 live betting situational playbooks |
| `environmental_impacts` | Venue-specific performance factors |
| `bankroll_phases` | Phase allocation framework |

### Key Player Metrics

- **Offensive:** goals, assists, shots, xG, xG/90, goals/90, shot accuracy
- **Passing:** passes completed/attempted, pass accuracy %, key passes, crosses
- **Defense:** tackles, interceptions, blocks, clearances, aerials won/lost
- **Discipline:** yellow/red cards, fouls committed/drawn, cards/90
- **Goalkeeping:** saves, goals conceded, psxg (post-shot xG)

---

## Makefile Commands

```bash
make help          # Show all available commands
make install       # Create venv and install dependencies
make build-all     # Full build: install + reports
make reports       # Generate all CSV reports
make tui           # Launch the interactive terminal UI (English)
make cli           # Launch the CLI
make clean         # Remove generated files and database
make test          # Run basic validation tests
```

---

## Extending for 2026

This repository is designed to grow as 2026 approaches:

1. **Squad Projections:** Populate `squad_projections_2026` with model-based likelihood scores for each player's 2026 squad inclusion.
2. **Odds Data:** Add a table for historical and live odds from The Odds API or Pinnacle.
3. **Weather Integration:** Enrich `venues_2026` with live matchday forecasts via OpenWeatherMap.
4. **Additional Tournaments:** Add Euro 2024, Copa América 2024, etc. for richer player form data.
5. **Transfermarkt Data:** Scrape market values and club performance for deeper squad valuation.

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for architecture details and contribution guidelines.

---

## Data Sources

| Source | Data | License |
|:---|:---|:---|
| **Smart Bet Field Guide** | Tier classifications, betting angles, scenarios | Original content |
| **Project Seed Data** | 2026 venue profiles, penalty takers, set-piece data | Hand-curated from public sources |

---

## Technology Stack

- **Python 3.10+**
- **SQLite** — local, zero-config database
- **Pandas** — data manipulation
- **Textual** — interactive terminal UI
- **Matplotlib / Seaborn** — visualization (optional)

---

## License

MIT License — See [LICENSE](LICENSE) for details.

> *Built for the Smart Bet Field Guide: FIFA 2026 project. All odds, regulatory references, and structural data reflect information available as of 2026. Always verify current odds, regulations, and squad information before placing wagers. Bet responsibly.*
