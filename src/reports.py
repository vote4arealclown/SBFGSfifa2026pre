"""
FIFA 2026 Data Repository - Reporting & Analytics Module
Run queries, generate reports, and export data for modeling.
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd

from database import get_connection

REPORTS_DIR = Path(__file__).parent.parent / "reports"


def _df_from_query(query: str, params=(), db_path: str = None) -> pd.DataFrame:
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn, params=params)


def report_top_scorers(limit: int = 20, db_path: str = None) -> pd.DataFrame:
    """Top goal scorers with per-90 rates."""
    query = """
        SELECT 
            p.player_name,
            t.team_name,
            p.position,
            p.matches_played,
            p.minutes_played,
            p.goals,
            ROUND(p.goals_per_90, 2) as goals_per_90,
            ROUND(p.xg, 2) as xg,
            ROUND(p.xg_per_90, 2) as xg_per_90,
            p.shots,
            p.shots_on_target,
            ROUND(CASE WHEN p.shots > 0 THEN p.shots_on_target * 100.0 / p.shots ELSE 0 END, 1) as shot_accuracy_pct
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.goals > 0
        ORDER BY p.goals DESC, p.goals_per_90 DESC
        LIMIT ?
    """
    return _df_from_query(query, (limit,), db_path)


def report_top_assisters(limit: int = 20, db_path: str = None) -> pd.DataFrame:
    """Top assist providers with key pass data."""
    query = """
        SELECT 
            p.player_name,
            t.team_name,
            p.position,
            p.matches_played,
            p.minutes_played,
            p.assists,
            ROUND(p.assists_per_90, 2) as assists_per_90,
            p.key_passes,
            p.crosses,
            ROUND(p.xg_assist, 2) as xg_assist,
            ROUND(p.xg_assist_per_90, 2) as xg_assist_per_90
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.assists > 0 OR p.key_passes > 5
        ORDER BY p.assists DESC, p.xg_assist DESC
        LIMIT ?
    """
    return _df_from_query(query, (limit,), db_path)


def report_top_xg_performers(limit: int = 20, db_path: str = None) -> pd.DataFrame:
    """Players sorted by expected goals (xG) output."""
    query = """
        SELECT 
            p.player_name,
            t.team_name,
            p.position,
            p.matches_played,
            p.minutes_played,
            ROUND(p.xg, 2) as xg,
            ROUND(p.xg_per_90, 2) as xg_per_90,
            p.goals,
            ROUND(p.goals - p.xg, 2) as goals_minus_xg,
            p.shots,
            p.shots_on_target
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.xg > 1.0
        ORDER BY p.xg DESC
        LIMIT ?
    """
    return _df_from_query(query, (limit,), db_path)


def report_defensive_leaders(limit: int = 20, db_path: str = None) -> pd.DataFrame:
    """Top defensive performers."""
    query = """
        SELECT 
            p.player_name,
            t.team_name,
            p.position,
            p.matches_played,
            p.minutes_played,
            p.tackles,
            p.tackles_won,
            p.interceptions,
            p.blocks,
            p.clearances,
            p.aerials_won,
            p.pressures,
            p.fouls_committed,
            p.yellow_cards,
            p.red_cards
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE (p.tackles + p.interceptions + p.blocks + p.clearances) > 5
        ORDER BY (p.tackles + p.interceptions + p.blocks) DESC
        LIMIT ?
    """
    return _df_from_query(query, (limit,), db_path)


def report_goalkeepers(limit: int = 20, db_path: str = None) -> pd.DataFrame:
    """Goalkeeper performance summary."""
    query = """
        SELECT 
            p.player_name,
            t.team_name,
            p.matches_played,
            p.minutes_played,
            p.saves,
            p.goals_conceded,
            ROUND(p.psxg, 2) as psxg,
            ROUND(CASE WHEN (p.saves + p.goals_conceded) > 0 
                 THEN p.saves * 100.0 / (p.saves + p.goals_conceded) ELSE 0 END, 1) as save_pct
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.position LIKE '%Goalkeeper%' OR p.saves > 0
        ORDER BY p.saves DESC
        LIMIT ?
    """
    return _df_from_query(query, (limit,), db_path)


def report_team_summary(db_path: str = None) -> pd.DataFrame:
    """Team-level aggregated statistics."""
    query = """
        SELECT 
            t.team_name,
            (SELECT COUNT(*) FROM matches m WHERE t.team_id IN (m.home_team_id, m.away_team_id)) as matches_played,
            (SELECT SUM(CASE WHEN m.home_team_id = t.team_id THEN m.home_score ELSE m.away_score END) 
             FROM matches m WHERE t.team_id IN (m.home_team_id, m.away_team_id)) as goals_for,
            (SELECT SUM(CASE WHEN m.home_team_id = t.team_id THEN m.away_score ELSE m.home_score END)
             FROM matches m WHERE t.team_id IN (m.home_team_id, m.away_team_id)) as goals_against,
            (SELECT SUM(CASE WHEN m.home_team_id = t.team_id AND m.home_score > m.away_score THEN 1
                             WHEN m.away_team_id = t.team_id AND m.away_score > m.home_score THEN 1 ELSE 0 END)
             FROM matches m WHERE t.team_id IN (m.home_team_id, m.away_team_id)) as wins,
            (SELECT SUM(CASE WHEN m.home_score = m.away_score THEN 1 ELSE 0 END)
             FROM matches m WHERE t.team_id IN (m.home_team_id, m.away_team_id)) as draws,
            (SELECT SUM(CASE WHEN m.home_team_id = t.team_id AND m.home_score < m.away_score THEN 1
                             WHEN m.away_team_id = t.team_id AND m.away_score < m.home_score THEN 1 ELSE 0 END)
             FROM matches m WHERE t.team_id IN (m.home_team_id, m.away_team_id)) as losses,
            (SELECT COUNT(DISTINCT p.player_id) FROM players p WHERE p.team_id = t.team_id) as squad_size,
            (SELECT SUM(p.goals) FROM players p WHERE p.team_id = t.team_id) as total_goals,
            (SELECT SUM(p.assists) FROM players p WHERE p.team_id = t.team_id) as total_assists,
            (SELECT ROUND(SUM(p.xg), 2) FROM players p WHERE p.team_id = t.team_id) as total_xg,
            (SELECT ROUND(AVG(p.age_at_tournament), 1) FROM players p WHERE p.team_id = t.team_id) as avg_age
        FROM teams t
        ORDER BY wins DESC, goals_for DESC
    """
    return _df_from_query(query, db_path=db_path)


def report_player_roster(
    team_name: str = None, position: str = None, db_path: str = None
) -> pd.DataFrame:
    """Full player roster with all available stats."""
    where_clauses = ["p.player_id IS NOT NULL"]
    params = []
    if team_name:
        where_clauses.append("t.team_name = ?")
        params.append(team_name)
    if position:
        where_clauses.append("p.position LIKE ?")
        params.append(f"%{position}%")

    where_str = " AND ".join(where_clauses)
    query = f"""
        SELECT 
            p.player_id,
            p.player_name,
            p.player_nickname,
            p.jersey_number,
            p.country,
            t.team_name,
            p.position,
            p.age_at_tournament,
            p.height_cm,
            p.foot,
            p.club_name,
            p.market_value_eur,
            p.is_captain,
            p.matches_played,
            p.minutes_played,
            p.goals,
            p.assists,
            p.own_goals,
            p.penalties_scored,
            p.shots,
            p.shots_on_target,
            ROUND(p.xg, 2) as xg,
            ROUND(p.xg_assist, 2) as xg_assist,
            p.passes_completed,
            p.passes_attempted,
            ROUND(p.pass_accuracy_pct, 1) as pass_accuracy_pct,
            p.progressive_passes,
            p.key_passes,
            p.crosses,
            p.dribbles_completed,
            p.tackles,
            p.tackles_won,
            p.interceptions,
            p.blocks,
            p.clearances,
            p.aerials_won,
            p.fouls_committed,
            p.fouls_drawn,
            p.yellow_cards,
            p.red_cards,
            p.saves,
            p.goals_conceded,
            p.clean_sheets,
            ROUND(p.goals_per_90, 2) as goals_per_90,
            ROUND(p.assists_per_90, 2) as assists_per_90,
            ROUND(p.xg_per_90, 2) as xg_per_90,
            ROUND(p.xg_assist_per_90, 2) as xg_assist_per_90,
            ROUND(p.cards_per_90, 2) as cards_per_90,
            p.likely_2026_squad,
            p.age_2026,
            p.projected_role_2026,
            p.notes
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE {where_str}
        ORDER BY t.team_name, p.position, p.player_name
    """
    return _df_from_query(query, tuple(params), db_path)


def export_all_reports(db_path: str = None, output_dir: str = None):
    """Generate and save all standard reports to CSV."""
    out = Path(output_dir or REPORTS_DIR)
    out.mkdir(parents=True, exist_ok=True)

    reports = {
        "top_scorers": report_top_scorers(50, db_path),
        "top_assisters": report_top_assisters(50, db_path),
        "top_xg": report_top_xg_performers(50, db_path),
        "defensive_leaders": report_defensive_leaders(50, db_path),
        "goalkeepers": report_goalkeepers(50, db_path),
        "team_summary": report_team_summary(db_path),
        "full_roster": report_player_roster(db_path=db_path),
        "team_tiers": report_team_tiers(db_path),
        "penalty_takers": report_penalty_takers(db_path),
        "set_piece_specialists": report_set_piece_specialists(db_path),
        "key_dates": report_key_dates(db_path),
        "checklist": report_checklist(db_path),
        "betting_scenarios": report_betting_scenarios(db_path),
        "environmental_impacts": report_environmental_impacts(db_path),
        "bankroll_phases": report_bankroll_phases(db_path),
        "glossary": report_glossary(db_path),
    }

    for name, df in reports.items():
        path = out / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  Saved {name}: {len(df)} rows -> {path}")

    return out


def get_player_profile(player_name: str, db_path: str = None) -> Dict[str, Any]:
    """Get a single player's comprehensive profile."""
    query = """
        SELECT * FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.player_name LIKE ?
        LIMIT 1
    """
    df = _df_from_query(query, (f"%{player_name}%",), db_path)
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


def search_players(query_str: str, db_path: str = None) -> pd.DataFrame:
    """Fuzzy search across player names, countries, clubs, positions."""
    q = f"%{query_str}%"
    query = """
        SELECT 
            p.player_name, t.team_name, p.position, 
            p.country, p.club_name, p.age_at_tournament,
            p.matches_played, p.minutes_played, p.goals, p.assists
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        WHERE p.player_name LIKE ? 
           OR p.country LIKE ? 
           OR p.club_name LIKE ?
           OR p.position LIKE ?
        ORDER BY p.goals DESC, p.minutes_played DESC
        LIMIT 50
    """
    return _df_from_query(query, (q, q, q, q), db_path)


# --- Field Guide Reference Reports ---


def report_team_tiers(db_path: str = None) -> pd.DataFrame:
    """Team tier classifications from the Field Guide."""
    query = """
        SELECT tier, team_name, odds_range, strengths, weaknesses, betting_angles, realistic_expectation
        FROM team_tiers
        ORDER BY 
            CASE tier 
                WHEN 'Tier 1: Favorites' THEN 1 
                WHEN 'Tier 2: Contenders' THEN 2 
                WHEN 'Tier 3: Host Nations' THEN 3 
                ELSE 4 
            END, team_name
    """
    return _df_from_query(query, db_path=db_path)


def report_penalty_takers(db_path: str = None) -> pd.DataFrame:
    """Penalty takers with conversion rates."""
    query = """
        SELECT player_name, team_name, 
            CASE WHEN is_primary THEN 'Primary' WHEN is_secondary THEN 'Secondary' ELSE '' END as role,
            conversion_rate_pct, career_penalties_scored, career_penalties_taken, notes
        FROM penalty_takers
        ORDER BY is_primary DESC, conversion_rate_pct DESC
    """
    return _df_from_query(query, db_path=db_path)


def report_set_piece_specialists(db_path: str = None) -> pd.DataFrame:
    """Set-piece takers (corners, free kicks, penalties)."""
    query = """
        SELECT player_name, team_name,
            CASE WHEN penalty_taker THEN 'Yes' ELSE '' END as penalties,
            CASE WHEN primary_free_kick THEN 'Primary' WHEN secondary_free_kick THEN 'Secondary' ELSE '' END as free_kicks,
            CASE WHEN primary_corner THEN 'Primary' WHEN secondary_corner THEN 'Secondary' ELSE '' END as corners,
            notes
        FROM set_piece_specialists
        ORDER BY team_name, player_name
    """
    return _df_from_query(query, db_path=db_path)


def report_key_dates(db_path: str = None) -> pd.DataFrame:
    """Key dates timeline for 2026."""
    query = """
        SELECT date_range, event_name, betting_action, priority
        FROM key_dates
        ORDER BY 
            CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 ELSE 3 END
    """
    return _df_from_query(query, db_path=db_path)


def report_checklist(db_path: str = None) -> pd.DataFrame:
    """Pre-tournament checklist."""
    query = """
        SELECT category, item, completed, priority, due_by
        FROM checklist_items
        ORDER BY 
            CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 ELSE 3 END,
            due_by
    """
    return _df_from_query(query, db_path=db_path)


def report_betting_scenarios(db_path: str = None) -> pd.DataFrame:
    """Live betting scenarios."""
    query = """
        SELECT scenario_name, phase, trigger, market_behavior, recommended_action, confidence
        FROM betting_scenarios
        ORDER BY 
            CASE confidence WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
    """
    return _df_from_query(query, db_path=db_path)


def report_environmental_impacts(db_path: str = None) -> pd.DataFrame:
    """Environmental factor matrix."""
    query = """
        SELECT factor, affected_venues, performance_impact, betting_market_implication
        FROM environmental_impacts
    """
    return _df_from_query(query, db_path=db_path)


def report_bankroll_phases(db_path: str = None) -> pd.DataFrame:
    """Bankroll phase allocation framework."""
    query = """
        SELECT phase, days, allocation_pct, daily_exposure_limit, strategic_focus
        FROM bankroll_phases
        ORDER BY allocation_pct DESC
    """
    return _df_from_query(query, db_path=db_path)


def report_glossary(db_path: str = None) -> pd.DataFrame:
    """Betting terminology glossary."""
    query = """
        SELECT term, definition, wc2026_relevance
        FROM betting_glossary
        ORDER BY term
    """
    return _df_from_query(query, db_path=db_path)


if __name__ == "__main__":
    print("Generating all reports...")
    export_all_reports()
    print("Done.")
