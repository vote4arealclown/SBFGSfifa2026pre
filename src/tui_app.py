#!/usr/bin/env python3
"""
Smart Bet Field Guide System 2026 — Interactive TUI
A terminal user interface for navigating reports, searching players,
exploring the World Cup 2022 dataset, and accessing Field Guide intelligence.

Run: python src/tui_app.py
"""

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static, Input, Footer, Header, Markdown
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding
import pandas as pd

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


class ReportScreen(Screen):
    """Screen that displays a pandas DataFrame in a DataTable."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]

    def __init__(self, title: str, df: pd.DataFrame, **kwargs):
        self.report_title = title
        self.df = df
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(
            f"[b]{self.report_title}[/b]  |  {len(self.df)} rows",
            classes="report-header",
        )
        table = DataTable(id="report_table", show_cursor=True, cursor_type="row")
        yield table
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#report_table", DataTable)
        table.clear(columns=True)
        if self.df.empty:
            table.add_columns("No Data")
            table.add_row("No data available for this report.")
            return

        for col in self.df.columns:
            table.add_column(str(col), key=str(col))

        display_df = self.df.head(500)
        for _, row in display_df.iterrows():
            table.add_row(*[self._fmt(v) for v in row.values])

    def _fmt(self, val) -> str:
        if pd.isna(val):
            return ""
        if isinstance(val, float):
            return f"{val:.2f}"
        return str(val)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#report_table", DataTable)
        row_key = event.row_key
        row = table.get_row(row_key)
        if row and self.report_title in (
            "Top Scorers",
            "Top xG Performers",
            "Top Assisters",
            "Defensive Leaders",
            "Goalkeepers",
            "Player Search",
            "Full Player Roster",
        ):
            player_name = str(row[0])
            self.app.push_screen(PlayerDetailScreen(player_name))


class PlayerDetailScreen(Screen):
    """Screen showing full player profile."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]

    def __init__(self, player_name: str, **kwargs):
        self.player_name = player_name
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(
            f"[b]Player Profile:[/b] {self.player_name}", classes="report-header"
        )
        yield Markdown(id="profile_md")
        yield Footer()

    def on_mount(self) -> None:
        profile = get_player_profile(self.player_name)
        md = self._profile_to_markdown(profile)
        self.query_one("#profile_md", Markdown).update(md)

    def _profile_to_markdown(self, profile: dict) -> str:
        if not profile:
            return "# Player not found"

        lines = [f"# {profile.get('player_name', 'Unknown')}"]
        if profile.get("player_nickname"):
            lines.append(f"*AKA: {profile['player_nickname']}*")
        lines.append("")

        lines.append("## Basic Info")
        for key in [
            "country",
            "team_name",
            "position",
            "jersey_number",
            "age_at_tournament",
        ]:
            if profile.get(key):
                lines.append(f"- **{key.replace('_', ' ').title()}:** {profile[key]}")
        lines.append("")

        lines.append("## 2022 Tournament Stats")
        stats = [
            ("matches_played", "Matches"),
            ("minutes_played", "Minutes"),
            ("goals", "Goals"),
            ("assists", "Assists"),
            ("shots", "Shots"),
            ("shots_on_target", "Shots on Target"),
            ("xg", "xG"),
            ("xg_per_90", "xG/90"),
            ("goals_per_90", "Goals/90"),
            ("assists_per_90", "Assists/90"),
            ("pass_accuracy_pct", "Pass Accuracy %"),
            ("passes_completed", "Passes Completed"),
            ("key_passes", "Key Passes"),
            ("dribbles_completed", "Dribbles Completed"),
            ("tackles", "Tackles"),
            ("interceptions", "Interceptions"),
            ("yellow_cards", "Yellow Cards"),
            ("red_cards", "Red Cards"),
        ]
        for key, label in stats:
            val = profile.get(key)
            if val is not None and val != 0:
                if isinstance(val, float):
                    lines.append(f"- **{label}:** {val:.2f}")
                else:
                    lines.append(f"- **{label}:** {val}")

        return "\n".join(lines)


class SearchScreen(Screen):
    """Player search screen."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(
            "[b]Player Search[/b]  |  Type a name, country, club, or position and press Enter",
            classes="report-header",
        )
        yield Input(placeholder="Search...", id="search_input")
        yield DataTable(id="search_results", show_cursor=True, cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search_input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return
        df = search_players(query)
        table = self.query_one("#search_results", DataTable)
        table.clear(columns=True)
        if df.empty:
            table.add_columns("Result")
            table.add_row("No players found.")
            return
        for col in df.columns:
            table.add_column(str(col), key=str(col))
        for _, row in df.head(100).iterrows():
            table.add_row(*[str(v) if pd.notna(v) else "" for v in row.values])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#search_results", DataTable)
        row_key = event.row_key
        row = table.get_row(row_key)
        if row:
            player_name = str(row[0])
            self.app.push_screen(PlayerDetailScreen(player_name))


class VenueScreen(Screen):
    """Screen showing 2026 venue data."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("[b]2026 World Cup Venues[/b]", classes="report-header")
        yield DataTable(id="venue_table", show_cursor=True, cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        with get_connection() as conn:
            df = pd.read_sql_query(
                """
                SELECT venue_name, city, country, capacity, altitude_m, climate_zone,
                       avg_june_temp_c, avg_july_temp_c, avg_humidity_pct
                FROM venues_2026 ORDER BY country, city
            """,
                conn,
            )

        table = self.query_one("#venue_table", DataTable)
        for col in df.columns:
            table.add_column(str(col).replace("_", " ").title(), key=str(col))
        for _, row in df.iterrows():
            table.add_row(*[str(v) if pd.notna(v) else "" for v in row.values])


class MarkdownReportScreen(Screen):
    """Screen that displays content as Markdown."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]

    def __init__(self, title: str, content: str, **kwargs):
        self.report_title = title
        self.content = content
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static(f"[b]{self.report_title}[/b]", classes="report-header")
        yield Markdown(id="md_content")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#md_content", Markdown).update(self.content)


class MainScreen(Screen):
    """Main menu screen with sidebar navigation."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "show_scorers", "Top Scorers"),
        Binding("2", "show_assisters", "Top Assisters"),
        Binding("3", "show_xg", "Top xG"),
        Binding("4", "show_defense", "Defense"),
        Binding("5", "show_keepers", "Goalkeepers"),
        Binding("6", "show_teams", "Teams"),
        Binding("7", "show_roster", "Roster"),
        Binding("8", "show_venues", "Venues"),
        Binding("9", "show_tiers", "Tiers"),
        Binding("0", "show_penalties", "Penalties"),
        Binding("p", "show_setpieces", "Set Pieces"),
        Binding("d", "show_dates", "Key Dates"),
        Binding("l", "show_checklist", "Checklist"),
        Binding("b", "show_scenarios", "Scenarios"),
        Binding("e", "show_environment", "Environment"),
        Binding("r", "show_bankroll", "Bankroll"),
        Binding("g", "show_glossary", "Glossary"),
        Binding("s", "show_search", "Search"),
        Binding("c", "show_counts", "DB Counts"),
    ]

    CSS = """
    Screen { align: center middle; }
    .main-container { width: 100%; height: 100%; }
    .sidebar { width: 32; height: 100%; background: $surface-darken-1; padding: 1; }
    .content { width: 1fr; height: 100%; padding: 1; }
    .title { text-align: center; margin-bottom: 1; color: $primary; }
    .menu-item { margin: 0; padding: 0; }
    .info-box { border: solid $primary; padding: 1; margin-top: 2; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(classes="main-container"):
            with Vertical(classes="sidebar"):
                yield Static(
                    "[b]SBFG 2026[/b]\nSmart Bet Field\nGuide System", classes="title"
                )
                yield Static("")
                yield Static("[u]Player Stats[/u]")
                yield Static("[b]1[/b]  Top Scorers", classes="menu-item")
                yield Static("[b]2[/b]  Top Assisters", classes="menu-item")
                yield Static("[b]3[/b]  Top xG", classes="menu-item")
                yield Static("[b]4[/b]  Defense", classes="menu-item")
                yield Static("[b]5[/b]  Goalkeepers", classes="menu-item")
                yield Static("")
                yield Static("[u]Team & Venue[/u]")
                yield Static("[b]6[/b]  Team Summary", classes="menu-item")
                yield Static("[b]7[/b]  Full Roster", classes="menu-item")
                yield Static("[b]8[/b]  2026 Venues", classes="menu-item")
                yield Static("[b]9[/b]  Team Tiers", classes="menu-item")
                yield Static("")
                yield Static("[u]Field Guide Intel[/u]")
                yield Static("[b]0[/b]  Penalty Takers", classes="menu-item")
                yield Static("[b]p[/b]  Set-Piece Specs", classes="menu-item")
                yield Static("[b]d[/b]  Key Dates", classes="menu-item")
                yield Static("[b]l[/b]  Checklist", classes="menu-item")
                yield Static("[b]b[/b]  Bet Scenarios", classes="menu-item")
                yield Static("[b]e[/b]  Environment", classes="menu-item")
                yield Static("[b]r[/b]  Bankroll", classes="menu-item")
                yield Static("[b]g[/b]  Glossary", classes="menu-item")
                yield Static("")
                yield Static("[u]Tools[/u]")
                yield Static("[b]s[/b]  Player Search", classes="menu-item")
                yield Static("[b]c[/b]  DB Counts", classes="menu-item")
                yield Static("")
                yield Static("[u]Nav[/u]")
                yield Static("[b]q[/b]  Quit", classes="menu-item")
            with Vertical(classes="content"):
                yield Static(
                    "[b]Smart Bet Field Guide System 2026[/b]\n", classes="title"
                )
                yield Static(
                    """
Navigate the complete FIFA World Cup 2022 dataset and
2026 betting intelligence using the sidebar keys.

[b]Dataset:[/b]
- 32 teams, 829 players, 64 matches
- ~7,400 key match events with xG
- 16 venue environmental profiles
- 11 team tier classifications
- 15 penalty takers identified
- 20 betting glossary terms
- 6 live betting scenarios
- 20 pre-tournament checklist items

[b]Quick Tips:[/b]
- Press [b]1-0[/b], [b]p-r[/b], [b]e-g[/b] for reports
- Press [b]s[/b] to search players
- Select any player row for full profile
- Press [b]Escape[/b] or [b]q[/b] to go back
                """.strip()
                )
                yield Static(id="counts_box", classes="info-box")
        yield Footer()

    def on_mount(self) -> None:
        self._update_counts()

    def _update_counts(self) -> None:
        counts = table_counts()
        lines = ["[b]Database Counts[/b]"]
        for t, c in counts.items():
            if c > 0:
                lines.append(f"  {t}: {c}")
        self.query_one("#counts_box", Static).update("\n".join(lines))

    def action_show_scorers(self) -> None:
        self.app.push_screen(ReportScreen("Top Scorers", report_top_scorers(100)))

    def action_show_assisters(self) -> None:
        self.app.push_screen(ReportScreen("Top Assisters", report_top_assisters(100)))

    def action_show_xg(self) -> None:
        self.app.push_screen(
            ReportScreen("Top xG Performers", report_top_xg_performers(100))
        )

    def action_show_defense(self) -> None:
        self.app.push_screen(
            ReportScreen("Defensive Leaders", report_defensive_leaders(100))
        )

    def action_show_keepers(self) -> None:
        self.app.push_screen(ReportScreen("Goalkeepers", report_goalkeepers(100)))

    def action_show_teams(self) -> None:
        self.app.push_screen(ReportScreen("Team Summary", report_team_summary()))

    def action_show_roster(self) -> None:
        self.app.push_screen(ReportScreen("Full Player Roster", report_player_roster()))

    def action_show_venues(self) -> None:
        self.app.push_screen(VenueScreen())

    def action_show_tiers(self) -> None:
        self.app.push_screen(ReportScreen("Team Tiers", report_team_tiers()))

    def action_show_penalties(self) -> None:
        self.app.push_screen(ReportScreen("Penalty Takers", report_penalty_takers()))

    def action_show_setpieces(self) -> None:
        self.app.push_screen(
            ReportScreen("Set-Piece Specialists", report_set_piece_specialists())
        )

    def action_show_dates(self) -> None:
        self.app.push_screen(ReportScreen("Key Dates", report_key_dates()))

    def action_show_checklist(self) -> None:
        self.app.push_screen(
            ReportScreen("Pre-Tournament Checklist", report_checklist())
        )

    def action_show_scenarios(self) -> None:
        self.app.push_screen(
            ReportScreen("Live Betting Scenarios", report_betting_scenarios())
        )

    def action_show_environment(self) -> None:
        self.app.push_screen(
            ReportScreen("Environmental Impact Matrix", report_environmental_impacts())
        )

    def action_show_bankroll(self) -> None:
        self.app.push_screen(
            ReportScreen("Bankroll Phase Allocations", report_bankroll_phases())
        )

    def action_show_glossary(self) -> None:
        self.app.push_screen(ReportScreen("Betting Glossary", report_glossary()))

    def action_show_search(self) -> None:
        self.app.push_screen(SearchScreen())

    def action_show_counts(self) -> None:
        self._update_counts()
        self.notify("Counts refreshed", title="Database")


class SBFG2026TUI(App):
    """Main TUI Application."""

    CSS = """
    Screen { align: center middle; }
    .report-header { height: 1; background: $primary-darken-2; color: $text; padding: 0 1; content-align: left middle; }
    DataTable { height: 1fr; border: solid $primary; }
    Input { margin: 1; }
    """

    def on_mount(self) -> None:
        self.push_screen(MainScreen())

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    app = SBFG2026TUI()
    app.run()
