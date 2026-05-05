#!/usr/bin/env python3
"""
Smart Bet Field Guide System 2026 — Command Line Interface
Quick queries and data exploration from the terminal.
"""

import sys
import argparse
from tabulate import tabulate

from database import get_connection, table_counts
from reports import (
    report_top_scorers,
    report_top_assisters,
    report_top_xg_performers,
    report_defensive_leaders,
    report_goalkeepers,
    report_team_summary,
    report_player_roster,
    search_players,
    get_player_profile,
    report_team_tiers,
    report_penalty_takers,
    report_set_piece_specialists,
    report_key_dates,
    report_checklist,
    report_betting_scenarios,
    report_environmental_impacts,
    report_bankroll_phases,
    report_glossary,
)
from betting_utils import parse_odds, kelly_criterion, clv_analysis, calculate_ev

REPORTS_DIR = "reports"


def _df_from_query(query: str, params=(), db_path: str = None):
    with get_connection(db_path) as conn:
        import pandas as pd

        return pd.read_sql_query(query, conn, params=params)


def cmd_counts(args):
    counts = table_counts()
    print("Smart Bet Field Guide System 2026 — Database Table Counts:")
    for t, c in counts.items():
        print(f"  {t:35s}: {c:6d}")


def cmd_top_scorers(args):
    df = report_top_scorers(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_top_assisters(args):
    df = report_top_assisters(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_top_xg(args):
    df = report_top_xg_performers(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_defense(args):
    df = report_defensive_leaders(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_keepers(args):
    df = report_goalkeepers(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_teams(args):
    df = report_team_summary()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_roster(args):
    df = report_player_roster(team_name=args.team, position=args.position)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_search(args):
    df = search_players(args.query)
    if df.empty:
        print(f"No players found matching '{args.query}'")
    else:
        print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_profile(args):
    profile = get_player_profile(args.name)
    if not profile:
        print(f"Player '{args.name}' not found.")
        return
    for key, val in profile.items():
        if val is not None and val != 0 and val != "":
            print(f"  {key}: {val}")


def cmd_venues(args):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT venue_name, city, country, capacity, altitude_m, climate_zone,
                   avg_june_temp_c, avg_july_temp_c, avg_humidity_pct
            FROM venues_2026 ORDER BY country, city
        """).fetchall()
        print(
            tabulate(
                [dict(r) for r in rows],
                headers="keys",
                tablefmt="grid",
                showindex=False,
            )
        )


def cmd_tiers(args):
    df = report_team_tiers()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_penalty_takers(args):
    df = report_penalty_takers()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_set_pieces(args):
    df = report_set_piece_specialists()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_key_dates(args):
    df = report_key_dates()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_checklist(args):
    df = report_checklist()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_scenarios(args):
    df = report_betting_scenarios()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_environment(args):
    df = report_environmental_impacts()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_bankroll(args):
    df = report_bankroll_phases()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_glossary(args):
    df = report_glossary()
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))


def cmd_odds(args):
    odds = parse_odds(args.value)
    print(f"Input: {args.value}")
    print(f"  Decimal:     {odds.decimal:.3f}")
    print(f"  American:    {odds.american:+d}")
    print(f"  Fractional:  {odds.fractional_num}/{odds.fractional_den}")
    print(f"  Implied Prob: {odds.implied_prob:.2%}")


def cmd_kelly(args):
    stake, rec = kelly_criterion(args.prob, args.odds, args.fraction)
    print(f"Model Probability: {args.prob:.1%}")
    print(f"Decimal Odds:      {args.odds:.2f}")
    print(f"Kelly Fraction:    {args.fraction:.0%}")
    print(f"Recommended Stake: {stake:.2%} of bankroll")
    print(f"Verdict: {rec}")


def cmd_clv(args):
    clv, rec = clv_analysis(args.entry, args.close)
    print(f"Entry Odds:   {args.entry:.2f}")
    print(f"Closing Odds: {args.close:.2f}")
    print(f"CLV:          {clv:+.2%}")
    print(f"Verdict:      {rec}")


def cmd_ev(args):
    ev, rec = calculate_ev(args.prob, args.odds)
    print(f"Model Probability: {args.prob:.1%}")
    print(f"Decimal Odds:      {args.odds:.2f}")
    print(f"Expected Value:    {ev:+.2%}")
    print(f"Verdict:           {rec}")


def cmd_export(args):
    import os
    from reports import export_all_reports

    os.makedirs(args.dir, exist_ok=True)
    export_all_reports(output_dir=args.dir)
    print(f"All reports exported to {args.dir}/")


def main():
    parser = argparse.ArgumentParser(
        description="Smart Bet Field Guide System 2026 — CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py counts
  python cli.py scorers --limit 10
  python cli.py tiers
  python cli.py penalties
  python cli.py odds --value +150
  python cli.py kelly --prob 0.42 --odds 2.50
  python cli.py roster --team "Argentina"
  python cli.py search "Mbappé"
  python cli.py profile --name "Messi"
  python cli.py venues
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    p_counts = subparsers.add_parser("counts", help="Show database table row counts")
    p_counts.set_defaults(func=cmd_counts)

    p_scorers = subparsers.add_parser("scorers", help="Top goal scorers")
    p_scorers.add_argument("--limit", type=int, default=20)
    p_scorers.set_defaults(func=cmd_top_scorers)

    p_assisters = subparsers.add_parser("assisters", help="Top assist providers")
    p_assisters.add_argument("--limit", type=int, default=20)
    p_assisters.set_defaults(func=cmd_top_assisters)

    p_xg = subparsers.add_parser("xg", help="Top xG performers")
    p_xg.add_argument("--limit", type=int, default=20)
    p_xg.set_defaults(func=cmd_top_xg)

    p_defense = subparsers.add_parser("defense", help="Top defensive performers")
    p_defense.add_argument("--limit", type=int, default=20)
    p_defense.set_defaults(func=cmd_defense)

    p_keepers = subparsers.add_parser("keepers", help="Goalkeeper stats")
    p_keepers.add_argument("--limit", type=int, default=20)
    p_keepers.set_defaults(func=cmd_keepers)

    p_teams = subparsers.add_parser("teams", help="Team summary stats")
    p_teams.set_defaults(func=cmd_teams)

    p_roster = subparsers.add_parser("roster", help="Player roster by team/position")
    p_roster.add_argument("--team", type=str, default=None)
    p_roster.add_argument("--position", type=str, default=None)
    p_roster.set_defaults(func=cmd_roster)

    p_search = subparsers.add_parser(
        "search", help="Search players by name/country/club"
    )
    p_search.add_argument("query", type=str)
    p_search.set_defaults(func=cmd_search)

    p_profile = subparsers.add_parser("profile", help="Full player profile")
    p_profile.add_argument("--name", type=str, required=True)
    p_profile.set_defaults(func=cmd_profile)

    p_venues = subparsers.add_parser("venues", help="2026 World Cup venue data")
    p_venues.set_defaults(func=cmd_venues)

    # Field Guide reference commands
    p_tiers = subparsers.add_parser("tiers", help="Team tier classifications")
    p_tiers.set_defaults(func=cmd_tiers)

    p_penalties = subparsers.add_parser("penalties", help="Penalty takers")
    p_penalties.set_defaults(func=cmd_penalty_takers)

    p_setpieces = subparsers.add_parser("setpieces", help="Set-piece specialists")
    p_setpieces.set_defaults(func=cmd_set_pieces)

    p_dates = subparsers.add_parser("dates", help="Key dates timeline")
    p_dates.set_defaults(func=cmd_key_dates)

    p_checklist = subparsers.add_parser("checklist", help="Pre-tournament checklist")
    p_checklist.set_defaults(func=cmd_checklist)

    p_scenarios = subparsers.add_parser("scenarios", help="Live betting scenarios")
    p_scenarios.set_defaults(func=cmd_scenarios)

    p_env = subparsers.add_parser("environment", help="Environmental impact matrix")
    p_env.set_defaults(func=cmd_environment)

    p_bankroll = subparsers.add_parser("bankroll", help="Bankroll phase allocations")
    p_bankroll.set_defaults(func=cmd_bankroll)

    p_glossary = subparsers.add_parser("glossary", help="Betting terminology glossary")
    p_glossary.set_defaults(func=cmd_glossary)

    # Betting utility commands
    p_odds = subparsers.add_parser("odds", help="Convert odds formats")
    p_odds.add_argument("--value", type=str, required=True, help="e.g. +150, 2.50, 6/4")
    p_odds.set_defaults(func=cmd_odds)

    p_kelly = subparsers.add_parser("kelly", help="Kelly Criterion bet sizing")
    p_kelly.add_argument(
        "--prob", type=float, required=True, help="Your estimated win probability (0-1)"
    )
    p_kelly.add_argument("--odds", type=float, required=True, help="Decimal odds")
    p_kelly.add_argument(
        "--fraction", type=float, default=0.25, help="Kelly fraction (default 0.25)"
    )
    p_kelly.set_defaults(func=cmd_kelly)

    p_clv = subparsers.add_parser("clv", help="Closing Line Value analysis")
    p_clv.add_argument("--entry", type=float, required=True, help="Entry decimal odds")
    p_clv.add_argument(
        "--close", type=float, required=True, help="Closing decimal odds"
    )
    p_clv.set_defaults(func=cmd_clv)

    p_ev = subparsers.add_parser("ev", help="Expected Value calculation")
    p_ev.add_argument(
        "--prob", type=float, required=True, help="Your estimated win probability (0-1)"
    )
    p_ev.add_argument("--odds", type=float, required=True, help="Decimal odds")
    p_ev.set_defaults(func=cmd_ev)

    p_export = subparsers.add_parser("export", help="Export all reports to CSV")
    p_export.add_argument("--dir", type=str, default="reports")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
