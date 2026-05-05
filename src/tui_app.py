#!/usr/bin/env python3
"""
Smart Bet Field Guide System 2026 — Interactive TUI
A terminal user interface for navigating reports, searching players,
exploring the World Cup 2022 dataset, and accessing Field Guide intelligence.

Run: python src/tui_app.py [--lang en|es]
"""

import argparse

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static, Input, Footer, Header, Markdown
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.binding import Binding
import pandas as pd

from i18n import Translator
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

    def __init__(
        self, title: str, df: pd.DataFrame, row_selectable: bool = False, **kwargs
    ):
        self.report_title = title
        self.df = df
        self.row_selectable = row_selectable
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        t = self.t
        yield Header(show_clock=False)
        yield Static(
            f"[b]{self.report_title}[/b]  |  {t.t('title_rows', n=len(self.df))}",
            classes="report-header",
        )
        table = DataTable(id="report_table", show_cursor=True, cursor_type="row")
        yield table
        yield Footer()

    def on_mount(self) -> None:
        t = self.app.translator
        table = self.query_one("#report_table", DataTable)
        table.clear(columns=True)
        if self.df.empty:
            table.add_columns(t.t("report_no_data"))
            table.add_row(t.t("report_no_data_msg"))
            return

        for col in self.df.columns:
            table.add_column(t.col(str(col)), key=str(col))

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
        if not self.row_selectable:
            return
        table = self.query_one("#report_table", DataTable)
        row_key = event.row_key
        row = table.get_row(row_key)
        if row:
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
        t = self.app.translator
        yield Header(show_clock=False)
        yield Static(
            f"[b]{t.t('title_profile')}:[/b] {self.player_name}",
            classes="report-header",
        )
        yield Markdown(id="profile_md")
        yield Footer()

    def on_mount(self) -> None:
        profile = get_player_profile(self.player_name)
        md = self._profile_to_markdown(profile)
        self.query_one("#profile_md", Markdown).update(md)

    def _profile_to_markdown(self, profile: dict) -> str:
        t = self.app.translator
        if not profile:
            return t.t("profile_not_found")

        lines = [f"# {profile.get('player_name', 'Unknown')}"]
        if profile.get("player_nickname"):
            lines.append(t.t("profile_aka", nickname=profile["player_nickname"]))
        lines.append("")

        lines.append(f"## {t.t('profile_basic_info')}")
        basic_keys = [
            ("country", "profile_country"),
            ("team_name", "profile_team"),
            ("position", "profile_position"),
            ("jersey_number", "profile_jersey"),
            ("age_at_tournament", "profile_age"),
        ]
        for key, label_key in basic_keys:
            if profile.get(key):
                lines.append(f"- **{t.t(label_key)}:** {profile[key]}")
        lines.append("")

        lines.append(f"## {t.t('profile_tournament_stats')}")
        stats = [
            ("matches_played", "stat_matches"),
            ("minutes_played", "stat_minutes"),
            ("goals", "stat_goals"),
            ("assists", "stat_assists"),
            ("shots", "stat_shots"),
            ("shots_on_target", "stat_shots_on_target"),
            ("xg", "stat_xg"),
            ("xg_per_90", "stat_xg_per_90"),
            ("goals_per_90", "stat_goals_per_90"),
            ("assists_per_90", "stat_assists_per_90"),
            ("pass_accuracy_pct", "stat_pass_accuracy"),
            ("passes_completed", "stat_passes_completed"),
            ("key_passes", "stat_key_passes"),
            ("dribbles_completed", "stat_dribbles"),
            ("tackles", "stat_tackles"),
            ("interceptions", "stat_interceptions"),
            ("yellow_cards", "stat_yellow"),
            ("red_cards", "stat_red"),
        ]
        for key, label_key in stats:
            val = profile.get(key)
            if val is not None and val != 0:
                if isinstance(val, float):
                    lines.append(f"- **{t.t(label_key)}:** {val:.2f}")
                else:
                    lines.append(f"- **{t.t(label_key)}:** {val}")

        return "\n".join(lines)


class SearchScreen(Screen):
    """Player search screen."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        t = self.app.translator
        yield Header(show_clock=False)
        yield Static(t.t("search_header"), classes="report-header")
        yield Input(placeholder=t.t("search_placeholder"), id="search_input")
        yield DataTable(id="search_results", show_cursor=True, cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search_input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        t = self.app.translator
        query = event.value.strip()
        if not query:
            return
        df = search_players(query)
        table = self.query_one("#search_results", DataTable)
        table.clear(columns=True)
        if df.empty:
            table.add_columns(t.t("search_result_col"))
            table.add_row(t.t("search_no_results"))
            return
        for col in df.columns:
            table.add_column(t.col(str(col)), key=str(col))
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
        t = self.app.translator
        yield Header(show_clock=False)
        yield Static(f"[b]{t.t('title_venues')}[/b]", classes="report-header")
        yield DataTable(id="venue_table", show_cursor=True, cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        t = self.app.translator
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
            table.add_column(t.col(str(col)), key=str(col))
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

    def __init__(self, translator: Translator = None, **kwargs):
        self._translator = translator
        self._build_bindings()
        super().__init__(**kwargs)

    @property
    def t(self) -> Translator:
        return self._translator or self.app.translator

    def _build_bindings(self):
        t = self.t
        self.BINDINGS = [
            Binding("q", "quit", t.t("bind_quit")),
            Binding("1", "show_scorers", t.t("bind_scorers")),
            Binding("2", "show_assisters", t.t("bind_assisters")),
            Binding("3", "show_xg", t.t("bind_xg")),
            Binding("4", "show_defense", t.t("bind_defense")),
            Binding("5", "show_keepers", t.t("bind_keepers")),
            Binding("6", "show_teams", t.t("bind_teams")),
            Binding("7", "show_roster", t.t("bind_roster")),
            Binding("8", "show_venues", t.t("bind_venues")),
            Binding("9", "show_tiers", t.t("bind_tiers")),
            Binding("0", "show_penalties", t.t("bind_penalties")),
            Binding("p", "show_setpieces", t.t("bind_setpieces")),
            Binding("d", "show_dates", t.t("bind_dates")),
            Binding("l", "show_checklist", t.t("bind_checklist")),
            Binding("b", "show_scenarios", t.t("bind_scenarios")),
            Binding("e", "show_environment", t.t("bind_environment")),
            Binding("r", "show_bankroll", t.t("bind_bankroll")),
            Binding("g", "show_glossary", t.t("bind_glossary")),
            Binding("s", "show_search", t.t("bind_search")),
            Binding("c", "show_counts", t.t("bind_counts")),
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
        t = self.app.translator
        yield Header(show_clock=False)
        with Horizontal(classes="main-container"):
            with Vertical(classes="sidebar"):
                yield Static(t.t("menu_title"), classes="title")
                yield Static("")
                yield Static(f"[u]{t.t('menu_player_stats')}[/u]")
                yield Static(f"[b]1[/b]  {t.t('menu_top_scorers')}", classes="menu-item")
                yield Static(f"[b]2[/b]  {t.t('menu_top_assisters')}", classes="menu-item")
                yield Static(f"[b]3[/b]  {t.t('menu_top_xg')}", classes="menu-item")
                yield Static(f"[b]4[/b]  {t.t('menu_defense')}", classes="menu-item")
                yield Static(f"[b]5[/b]  {t.t('menu_keepers')}", classes="menu-item")
                yield Static("")
                yield Static(f"[u]{t.t('menu_team_venue')}[/u]")
                yield Static(f"[b]6[/b]  {t.t('menu_team_summary')}", classes="menu-item")
                yield Static(f"[b]7[/b]  {t.t('menu_full_roster')}", classes="menu-item")
                yield Static(f"[b]8[/b]  {t.t('menu_venues')}", classes="menu-item")
                yield Static(f"[b]9[/b]  {t.t('menu_tiers')}", classes="menu-item")
                yield Static("")
                yield Static(f"[u]{t.t('menu_intel')}[/u]")
                yield Static(f"[b]0[/b]  {t.t('menu_penalties')}", classes="menu-item")
                yield Static(f"[b]p[/b]  {t.t('menu_setpieces')}", classes="menu-item")
                yield Static(f"[b]d[/b]  {t.t('menu_dates')}", classes="menu-item")
                yield Static(f"[b]l[/b]  {t.t('menu_checklist')}", classes="menu-item")
                yield Static(f"[b]b[/b]  {t.t('menu_scenarios')}", classes="menu-item")
                yield Static(f"[b]e[/b]  {t.t('menu_environment')}", classes="menu-item")
                yield Static(f"[b]r[/b]  {t.t('menu_bankroll')}", classes="menu-item")
                yield Static(f"[b]g[/b]  {t.t('menu_glossary')}", classes="menu-item")
                yield Static("")
                yield Static(f"[u]{t.t('menu_tools')}[/u]")
                yield Static(f"[b]s[/b]  {t.t('menu_player_search')}", classes="menu-item")
                yield Static(f"[b]c[/b]  {t.t('menu_db_counts')}", classes="menu-item")
                yield Static("")
                yield Static(f"[u]{t.t('menu_nav')}[/u]")
                yield Static(f"[b]q[/b]  {t.t('menu_quit')}", classes="menu-item")
            with Vertical(classes="content"):
                yield Static(t.t("main_header"), classes="title")
                yield Static(t.t("main_body"))
                yield Static(id="counts_box", classes="info-box")
        yield Footer()

    def on_mount(self) -> None:
        self._update_counts()

    def _update_counts(self) -> None:
        t = self.t
        counts = table_counts()
        lines = [f"[b]{t.t('counts_header')}[/b]"]
        for table_name, count in counts.items():
            if count > 0:
                lines.append(f"  {table_name}: {count}")
        self.query_one("#counts_box", Static).update("\n".join(lines))

    def action_show_scorers(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(t.t("title_scorers"), report_top_scorers(100), row_selectable=True)
        )

    def action_show_assisters(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(
                t.t("title_assisters"), report_top_assisters(100), row_selectable=True
            )
        )

    def action_show_xg(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(
                t.t("title_xg"), report_top_xg_performers(100), row_selectable=True
            )
        )

    def action_show_defense(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(
                t.t("title_defense"), report_defensive_leaders(100), row_selectable=True
            )
        )

    def action_show_keepers(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(
                t.t("title_keepers"), report_goalkeepers(100), row_selectable=True
            )
        )

    def action_show_teams(self) -> None:
        t = self.t
        self.app.push_screen(ReportScreen(t.t("title_teams"), report_team_summary()))

    def action_show_roster(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(
                t.t("title_roster"), report_player_roster(), row_selectable=True
            )
        )

    def action_show_venues(self) -> None:
        self.app.push_screen(VenueScreen())

    def action_show_tiers(self) -> None:
        t = self.t
        self.app.push_screen(ReportScreen(t.t("title_tiers"), report_team_tiers()))

    def action_show_penalties(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(t.t("title_penalties"), report_penalty_takers())
        )

    def action_show_setpieces(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(
                t.t("title_setpieces"), report_set_piece_specialists()
            )
        )

    def action_show_dates(self) -> None:
        t = self.t
        self.app.push_screen(ReportScreen(t.t("title_dates"), report_key_dates()))

    def action_show_checklist(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(t.t("title_checklist"), report_checklist())
        )

    def action_show_scenarios(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(t.t("title_scenarios"), report_betting_scenarios())
        )

    def action_show_environment(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(t.t("title_environment"), report_environmental_impacts())
        )

    def action_show_bankroll(self) -> None:
        t = self.t
        self.app.push_screen(
            ReportScreen(t.t("title_bankroll"), report_bankroll_phases())
        )

    def action_show_glossary(self) -> None:
        t = self.t
        self.app.push_screen(ReportScreen(t.t("title_glossary"), report_glossary()))

    def action_show_search(self) -> None:
        self.app.push_screen(SearchScreen())

    def action_show_counts(self) -> None:
        self._update_counts()
        t = self.t
        self.notify(t.t("notify_counts_refreshed"), title=t.t("notify_db"))


class SBFG2026TUI(App):
    """Main TUI Application."""

    CSS = """
    Screen { align: center middle; }
    .report-header { height: 1; background: $primary-darken-2; color: $text; padding: 0 1; content-align: left middle; }
    DataTable { height: 1fr; border: solid $primary; }
    Input { margin: 1; }
    """

    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.translator = Translator(lang)
        super().__init__()

    def on_mount(self) -> None:
        self.push_screen(MainScreen(translator=self.translator))

    def action_quit(self) -> None:
        self.exit()


def main():
    parser = argparse.ArgumentParser(description="SBFG2026 TUI")
    parser.add_argument("--lang", choices=["en", "es"], default="en", help="UI language")
    args = parser.parse_args()
    app = SBFG2026TUI(lang=args.lang)
    app.run()


if __name__ == "__main__":
    main()
