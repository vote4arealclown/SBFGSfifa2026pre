"""
FIFA 2026 Data Repository - Database Schema and Connection Manager
SQLite-based local database for comprehensive World Cup data.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data" / "fifa2026_repo.db"

SCHEMA_SQL = """
-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT NOT NULL UNIQUE,
    team_gender TEXT,
    team_group TEXT,
    confederation TEXT,
    fifa_ranking INTEGER,
    market_value_eur REAL,
    flag_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Players table (comprehensive roster)
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL,
    player_nickname TEXT,
    jersey_number INTEGER,
    country TEXT,
    team_id INTEGER,
    position TEXT,
    sub_position TEXT,
    date_of_birth TEXT,
    age_at_tournament REAL,
    height_cm INTEGER,
    foot TEXT,
    club_name TEXT,
    club_country TEXT,
    market_value_eur REAL,
    is_captain BOOLEAN DEFAULT 0,
    is_goalkeeper BOOLEAN DEFAULT 0,
    -- FIFA 2022 tournament stats
    matches_played INTEGER DEFAULT 0,
    minutes_played INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    own_goals INTEGER DEFAULT 0,
    penalties_scored INTEGER DEFAULT 0,
    penalties_missed INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    xg REAL DEFAULT 0,
    xg_assist REAL DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    passes_attempted INTEGER DEFAULT 0,
    pass_accuracy REAL DEFAULT 0,
    progressive_passes INTEGER DEFAULT 0,
    key_passes INTEGER DEFAULT 0,
    crosses INTEGER DEFAULT 0,
    dribbles_completed INTEGER DEFAULT 0,
    dribbles_attempted INTEGER DEFAULT 0,
    tackles INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    aerials_won INTEGER DEFAULT 0,
    aerials_lost INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,
    fouls_drawn INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    clean_sheets INTEGER DEFAULT 0,
    save_percentage REAL DEFAULT 0,
    psxg REAL DEFAULT 0,
    -- Derived metrics
    goals_per_90 REAL DEFAULT 0,
    assists_per_90 REAL DEFAULT 0,
    xg_per_90 REAL DEFAULT 0,
    xg_assist_per_90 REAL DEFAULT 0,
    cards_per_90 REAL DEFAULT 0,
    pass_accuracy_pct REAL DEFAULT 0,
    progressive_carries INTEGER DEFAULT 0,
    distance_carried REAL DEFAULT 0,
    pressures INTEGER DEFAULT 0,
    pressure_regain_pct REAL DEFAULT 0,
    -- 2026 projection flags
    likely_2026_squad BOOLEAN DEFAULT 0,
    age_2026 REAL,
    projected_role_2026 TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    match_date TEXT,
    kick_off TEXT,
    competition TEXT,
    season TEXT,
    match_week INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    home_penalties INTEGER,
    away_penalties INTEGER,
    match_status TEXT,
    match_status_360 TEXT,
    last_updated TEXT,
    last_updated_360 TEXT,
    metadata TEXT,
    competition_stage TEXT,
    stadium TEXT,
    referee TEXT,
    -- xG totals
    home_xg REAL,
    away_xg REAL,
    -- Weather / environmental (to be enriched)
    temperature_c REAL,
    humidity_pct REAL,
    altitude_m INTEGER,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

-- Match events (lineup, goals, cards, subs, etc.)
CREATE TABLE IF NOT EXISTS match_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    event_type TEXT,
    event_subtype TEXT,
    period INTEGER,
    timestamp TEXT,
    minute INTEGER,
    second INTEGER,
    player_id INTEGER,
    player_name TEXT,
    team_id INTEGER,
    team_name TEXT,
    position TEXT,
    formation TEXT,
    -- Event-specific JSON blob for flexibility
    event_data TEXT,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Player match-level stats (granular)
CREATE TABLE IF NOT EXISTS player_match_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    player_id INTEGER,
    team_id INTEGER,
    minutes_played INTEGER DEFAULT 0,
    -- Offensive
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    xg REAL DEFAULT 0,
    xg_np REAL DEFAULT 0,
    xg_assist REAL DEFAULT 0,
    -- Passing
    passes_completed INTEGER DEFAULT 0,
    passes_attempted INTEGER DEFAULT 0,
    progressive_passes INTEGER DEFAULT 0,
    key_passes INTEGER DEFAULT 0,
    crosses INTEGER DEFAULT 0,
    -- Dribbling
    dribbles_completed INTEGER DEFAULT 0,
    dribbles_attempted INTEGER DEFAULT 0,
    carries INTEGER DEFAULT 0,
    progressive_carries INTEGER DEFAULT 0,
    -- Defensive
    tackles INTEGER DEFAULT 0,
    tackles_won INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    aerials_won INTEGER DEFAULT 0,
    aerials_lost INTEGER DEFAULT 0,
    pressures INTEGER DEFAULT 0,
    pressure_regain_pct REAL DEFAULT 0,
    -- Discipline
    fouls_committed INTEGER DEFAULT 0,
    fouls_drawn INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    -- Goalkeeping
    saves INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    shots_faced INTEGER DEFAULT 0,
    psxg REAL DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    UNIQUE(match_id, player_id)
);

-- Team match-level stats
CREATE TABLE IF NOT EXISTS team_match_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    team_id INTEGER,
    goals INTEGER DEFAULT 0,
    xg REAL DEFAULT 0,
    shots INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,
    passes_completed INTEGER DEFAULT 0,
    passes_attempted INTEGER DEFAULT 0,
    possession_pct REAL DEFAULT 0,
    corners INTEGER DEFAULT 0,
    fouls INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    tackles INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    clearances INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    UNIQUE(match_id, team_id)
);

-- Lineups per match
CREATE TABLE IF NOT EXISTS match_lineups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER,
    team_id INTEGER,
    player_id INTEGER,
    player_name TEXT,
    jersey_number INTEGER,
    position TEXT,
    formation TEXT,
    starter BOOLEAN DEFAULT 0,
    minutes_played INTEGER DEFAULT 0,
    substituted_in INTEGER,
    substituted_out INTEGER,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- 2026 Squad Projections (manual or model-based)
CREATE TABLE IF NOT EXISTS squad_projections_2026 (
    projection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER,
    player_id INTEGER,
    projected_status TEXT, -- 'likely', 'bubble', 'longshot', 'retired', 'emerging'
    projected_starter BOOLEAN DEFAULT 0,
    projected_minutes INTEGER,
    projected_goals REAL,
    projected_assists REAL,
    confidence_score REAL,
    data_source TEXT,
    notes TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Venue / stadium reference for 2026
CREATE TABLE IF NOT EXISTS venues_2026 (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT NOT NULL UNIQUE,
    city TEXT,
    country TEXT,
    capacity INTEGER,
    altitude_m INTEGER,
    latitude REAL,
    longitude REAL,
    climate_zone TEXT,
    avg_june_temp_c REAL,
    avg_july_temp_c REAL,
    avg_humidity_pct REAL,
    grass_type TEXT,
    roof_type TEXT,
    home_teams TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team_id);
CREATE INDEX IF NOT EXISTS idx_players_country ON players(country);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_competition ON matches(competition);
CREATE INDEX IF NOT EXISTS idx_events_match ON match_events(match_id);
CREATE INDEX IF NOT EXISTS idx_events_player ON match_events(player_id);
CREATE INDEX IF NOT EXISTS idx_pm_stats_match ON player_match_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_pm_stats_player ON player_match_stats(player_id);
CREATE INDEX IF NOT EXISTS idx_tm_stats_match ON team_match_stats(match_id);
CREATE INDEX IF NOT EXISTS idx_lineups_match ON match_lineups(match_id);
CREATE INDEX IF NOT EXISTS idx_squad_proj_team ON squad_projections_2026(team_id);
CREATE INDEX IF NOT EXISTS idx_squad_proj_player ON squad_projections_2026(player_id);
"""


def init_database(db_path: str = None) -> str:
    """Initialize the SQLite database with full schema."""
    path = db_path or str(DB_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    return path


@contextmanager
def get_connection(db_path: str = None):
    """Context manager for database connections."""
    path = db_path or str(DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute(query: str, params=(), db_path: str = None):
    """Execute a query and return results."""
    with get_connection(db_path) as conn:
        cursor = conn.execute(query, params)
        return cursor.fetchall()


def execute_many(query: str, params_list, db_path: str = None):
    """Execute a query with many parameter sets."""
    with get_connection(db_path) as conn:
        conn.executemany(query, params_list)
        conn.commit()


def table_counts(db_path: str = None) -> dict:
    """Return row counts for all main tables."""
    tables = [
        "teams",
        "players",
        "matches",
        "match_events",
        "player_match_stats",
        "team_match_stats",
        "match_lineups",
        "squad_projections_2026",
        "venues_2026",
    ]
    counts = {}
    with get_connection(db_path) as conn:
        for t in tables:
            row = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()
            counts[t] = row[0]
    return counts


if __name__ == "__main__":
    db = init_database()
    print(f"Database initialized at: {db}")
    counts = table_counts(db)
    for t, c in counts.items():
        print(f"  {t}: {c} rows")
