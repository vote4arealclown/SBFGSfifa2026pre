"""
Smart Bet Field Guide System 2026 — Reference Data Seeding
Populates the database with analytical frameworks, checklists, glossary,
and betting intelligence from the Field Guide.
"""

from database import get_connection, execute_many


def create_reference_tables(db_path: str = None):
    """Add reference tables for Field Guide data."""
    sql = """
    -- Team tier classifications (from Field Guide Section 4)
    CREATE TABLE IF NOT EXISTS team_tiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT,
        tier TEXT, -- 'Tier 1: Favorites', 'Tier 2: Contenders', etc.
        odds_range TEXT,
        strengths TEXT,
        weaknesses TEXT,
        betting_angles TEXT,
        realistic_expectation TEXT,
        projected_2026_path TEXT,
        notes TEXT
    );

    -- Penalty takers (critical for player prop modeling)
    CREATE TABLE IF NOT EXISTS penalty_takers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        player_name TEXT,
        team_name TEXT,
        is_primary BOOLEAN DEFAULT 1,
        is_secondary BOOLEAN DEFAULT 0,
        conversion_rate_pct REAL,
        career_penalties_scored INTEGER,
        career_penalties_taken INTEGER,
        notes TEXT,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    );

    -- Set-piece specialists (corners, free kicks)
    CREATE TABLE IF NOT EXISTS set_piece_specialists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        player_name TEXT,
        team_name TEXT,
        penalty_taker INTEGER DEFAULT 0,
        primary_free_kick INTEGER DEFAULT 0,
        secondary_free_kick INTEGER DEFAULT 0,
        primary_corner INTEGER DEFAULT 0,
        secondary_corner INTEGER DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (player_id) REFERENCES players(player_id)
    );

    -- Betting terminology glossary
    CREATE TABLE IF NOT EXISTS betting_glossary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT UNIQUE,
        definition TEXT,
        wc2026_relevance TEXT
    );

    -- Key dates timeline
    CREATE TABLE IF NOT EXISTS key_dates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_range TEXT,
        event_name TEXT,
        betting_action TEXT,
        priority TEXT DEFAULT 'normal' -- critical, high, normal
    );

    -- Pre-tournament checklist
    CREATE TABLE IF NOT EXISTS checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT, -- Account Setup, Information Infrastructure, Strategic Preparation, Jurisdictional Awareness
        item TEXT,
        completed BOOLEAN DEFAULT 0,
        priority TEXT DEFAULT 'normal',
        due_by TEXT
    );

    -- Live betting scenarios (from Field Guide Section 9)
    CREATE TABLE IF NOT EXISTS betting_scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scenario_name TEXT,
        phase TEXT, -- Group Stage, Knockout, Live
        trigger TEXT,
        market_behavior TEXT,
        recommended_action TEXT,
        confidence TEXT
    );

    -- Environmental impact matrix
    CREATE TABLE IF NOT EXISTS environmental_impacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factor TEXT,
        affected_venues TEXT,
        performance_impact TEXT,
        betting_market_implication TEXT
    );

    -- Bankroll phase allocations
    CREATE TABLE IF NOT EXISTS bankroll_phases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phase TEXT,
        days TEXT,
        allocation_pct INTEGER,
        daily_exposure_limit TEXT,
        strategic_focus TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_tiers_team ON team_tiers(team_name);
    CREATE INDEX IF NOT EXISTS idx_penalty_team ON penalty_takers(team_name);
    CREATE INDEX IF NOT EXISTS idx_setpiece_team ON set_piece_specialists(team_name);
    """
    with get_connection(db_path) as conn:
        conn.executescript(sql)
        conn.commit()
    print("Reference tables created.")


def seed_team_tiers(db_path: str = None):
    """Seed team tier classifications from the Field Guide."""
    tiers = [
        # Tier 1: Favorites
        (
            "Spain",
            "Tier 1: Favorites",
            "+400 to +450",
            "Technical superiority in possession, tactical flexibility, deep talent pool, proven tournament-winning pedigree",
            "Market pricing reflects peak efficiency; expanded format demands physical resilience",
            "Avoid outright at current prices. Target group winner markets. Player props on creative midfielders. Contrarian value on AH underdogs when environmental factors apply.",
            "Semifinal minimum",
            "Deep run expected; physical demands of 8-match path are the main risk",
        ),
        (
            "England",
            "Tier 1: Favorites",
            "+500 to +650",
            "Tactical discipline under Tuchel, set-piece excellence, squad depth across Premier League and Europe, physicality suited to NA conditions",
            "Historical underperformance relative to talent; public money inflates prices; adaptation time needed",
            "Set-piece and corner markets. Each-way outright. Matchday 1 caution. Under totals in knockout matches.",
            "Quarterfinal to semifinal",
            "Round of 32 helps find rhythm; final remains 50/50 against elite",
        ),
        (
            "France",
            "Tier 1: Favorites",
            "+550 to +650",
            "Unparalleled athletic depth, tactical versatility, tournament experience at every position, ideal physical profile for summer NA conditions",
            "Managerial instability; squad harmony questions; psychological toll of consecutive final defeats",
            "Outright value if market overweights 2022 disappointment. Stage of elimination markets. Player props on athletic forwards. Card markets.",
            "Quarterfinal to final",
            "Depth is the single biggest structural advantage in 48-team format",
        ),
        (
            "Argentina",
            "Tier 1: Favorites",
            "+700 to +850",
            "Tournament-winning experience, Messi's decisive quality, cohesive squad identity, South American qualifying experience in varied climates",
            "Aging core; Messi dependency; potential emotional exhaustion; heat/humidity stress on older squad members",
            "Narrative inflation alert—avoid inflated prices. Group stage overs vs debutant defenses. Live betting on second-half substitutions.",
            "Round of 16 to quarterfinal",
            "Expanded format helps manage Messi's minutes; repeating is difficult",
        ),
        (
            "Brazil",
            "Tier 1: Favorites",
            "+750 to +850",
            "Exceptional individual talent across attacking positions, CONMEBOL qualifying experience, deep squad rotation options",
            "Managerial uncertainty; difficulty translating club chemistry to national team; tactical conservatism in knockouts",
            "Pre-tournament outright if prices drift to +900. Group stage AH caution. Under totals in knockout rounds. Player props on attacking midfielders.",
            "Quarterfinal to semifinal",
            "Has the talent but hasn't demonstrated tactical consistency of Spain or France",
        ),
        # Tier 2: Contenders & Dark Horses
        (
            "Portugal",
            "Tier 2: Contenders",
            "+1200",
            "Elite individual talent, increasing squad depth",
            "Managerial decision-making inconsistent in tournament contexts",
            "Group winner + outright each-way if favorable draw. Monitor veteran vs youth balance.",
            "Round of 16 to quarterfinal",
            "Favorable path dependent on draw",
        ),
        (
            "Germany",
            "Tier 2: Contenders",
            "+1400",
            "Historic power in tactical transition; physicality and organization suit NA conditions",
            "Post-2018 decline narrative may overweight recent disappointment",
            "Long-shot outright value. Group winner markets better than outright.",
            "Round of 16 to quarterfinal",
            "Home-continent advantage analogue from 2006",
        ),
        (
            "Italy",
            "Tier 2: Contenders",
            "+1600",
            "Defensive organization and tactical flexibility remain elite",
            "Attacking firepower questions persist",
            "Knockout stage under totals vs possession-dominant opponents. Low-block produces narrow score distributions.",
            "Round of 16 to quarterfinal",
            "Defensive solidity wins in low-scoring environments",
        ),
        # Tier 3: Host Nations
        (
            "United States",
            "Tier 3: Host Nations",
            None,
            "Home conditions; MLS-based squad familiarity with NA summer climates and travel",
            "Public money inflation on host nation markets; thin squad depth for 8-match load",
            "Geographic clustering advantage if group draws are regional. Team props on set pieces. Avoid match-winner markets.",
            "Group advancement as 2nd or 3rd. Round of 32 exit likely vs Tier 1.",
            "Host status creates 10-20% price inflation",
        ),
        (
            "Mexico",
            "Tier 3: Host Nations",
            None,
            "Opening match at Estadio Azteca; altitude familiarity; heritage advantage",
            "Evolving gambling regulatory environment in Mexico creates integrity concerns",
            "Altitude advantage—under totals in Mexico City matches. Matchday 1 value from home-equivalent status.",
            "Group stage advancement. Round of 32 competitive depending on draw.",
            "2,240m elevation is a genuine performance variable",
        ),
        (
            "Canada",
            "Tier 3: Host Nations",
            None,
            "Qualifying experience and technical improvement; temperate maritime conditions favor technical play",
            "Thin squad depth may force maximum minutes early; fatigue-driven underperformance in Matchday 3",
            "Undervaluation in markets— lacks historical pedigree. Climate advantage in Vancouver/Toronto.",
            "Third-place contention with goal difference. Round of 32 would exceed precedent.",
            "Public money ignores regional improvement",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO team_tiers
        (team_name, tier, odds_range, strengths, weaknesses, betting_angles, realistic_expectation, projected_2026_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_many(query, tiers, db_path)
    print(f"  -> {len(tiers)} team tiers seeded")


def seed_penalty_takers(db_path: str = None):
    """Seed known penalty takers from 2022 and projected 2026."""
    takers = [
        # Format: (player_name, team_name, is_primary, is_secondary, conversion_rate, career_scored, career_taken, notes)
        (
            "Lionel Messi",
            "Argentina",
            1,
            0,
            78.0,
            106,
            136,
            "Primary PK taker; VAR penalty expansion amplifies his anytime goalscorer value",
        ),
        (
            "Kylian Mbappé",
            "France",
            1,
            0,
            85.0,
            30,
            35,
            "Designated taker for France; elite conversion rate",
        ),
        (
            "Harry Kane",
            "England",
            1,
            0,
            84.0,
            60,
            71,
            "World-class penalty record; set-piece excellence adds corner/aerial threat",
        ),
        (
            "Cristiano Ronaldo",
            "Portugal",
            1,
            0,
            84.0,
            160,
            190,
            "All-time PK leader; age may reduce minutes but not role clarity",
        ),
        (
            "Bruno Fernandes",
            "Portugal",
            0,
            1,
            82.0,
            25,
            30,
            "Secondary taker for Portugal; primary when Ronaldo rests",
        ),
        (
            "Neymar",
            "Brazil",
            1,
            0,
            80.0,
            45,
            56,
            "Primary taker when fit; injury risk is main variable",
        ),
        ("Olivier Giroud", "France", 0, 1, 76.0, 20, 26, "Secondary option for France"),
        (
            "Lautaro Martínez",
            "Argentina",
            0,
            1,
            75.0,
            15,
            20,
            "Secondary option behind Messi",
        ),
        ("Álvaro Morata", "Spain", 1, 0, 74.0, 22, 30, "Primary taker for Spain"),
        (
            "Memphis Depay",
            "Netherlands",
            1,
            0,
            77.0,
            28,
            36,
            "Primary taker for Netherlands",
        ),
        ("Romelu Lukaku", "Belgium", 1, 0, 73.0, 35, 48, "Primary taker when selected"),
        (
            "Robert Lewandowski",
            "Poland",
            1,
            0,
            83.0,
            55,
            66,
            "Elite conversion; team may not qualify",
        ),
        (
            "Christian Pulisic",
            "United States",
            1,
            0,
            72.0,
            8,
            11,
            "Primary taker for USA",
        ),
        (
            "Raheem Sterling",
            "England",
            0,
            1,
            70.0,
            12,
            17,
            "Occasional taker for England",
        ),
        (
            "Mohamed Salah",
            "Egypt",
            1,
            0,
            86.0,
            35,
            41,
            "World-class conversion; team qualification uncertain",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO penalty_takers
        (player_name, team_name, is_primary, is_secondary, conversion_rate_pct, career_penalties_scored, career_penalties_taken, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_many(query, takers, db_path)
    print(f"  -> {len(takers)} penalty takers seeded")


def seed_betting_glossary(db_path: str = None):
    """Seed the betting terminology glossary."""
    terms = [
        (
            "Asian Handicap",
            "Goal handicap eliminating draw possibility",
            "Lower bookmaker margins than 1X2 markets; preferred vehicle for sharp bettors",
        ),
        (
            "BTTS",
            "Both Teams To Score (Yes/No)",
            "Third-place advancement affects motivation patterns; Matchday 3 scenarios create predictable patterns",
        ),
        (
            "Closing Line Value (CLV)",
            "Relationship between bet entry and final odds",
            "Primary predictor of long-term profitability; systematic CLV achievement indicates +EV betting",
        ),
        (
            "Expected Goals (xG)",
            "Quality assessment of goal-scoring chances",
            "Tournament-specific environmental adjustments required; fundamental analysis tool for totals and team performance",
        ),
        (
            "Round of 32",
            "New knockout stage introduced in 2026 format",
            "No historical World Cup data for pricing models; temporary market inefficiency before learning occurs",
        ),
        (
            "Best Third-Place",
            "Eight third-place teams advancing from 12 groups",
            "66.7% advancement rate vs. traditional 50%; softer qualification threshold affects motivation markets",
        ),
        (
            "Implied Probability",
            "Probability derived from odds format",
            "Essential for converting bookmaker prices into estimable value",
        ),
        (
            "Kelly Criterion",
            "Mathematical formula for optimal bet sizing",
            "Critical for hedging futures positions and determining bankroll allocation",
        ),
        (
            "Player Props",
            "Individual performance markets (goals, assists, cards, shots)",
            "Expanded field creates more mismatch opportunities; penalty taker identification provides structural advantage",
        ),
        (
            "Vigorish / Juice",
            "Bookmaker commission built into odds",
            "Asian Handicap markets offer 1.5-2.0% vs. 4-5% in 1X2—significant long-term impact",
        ),
        (
            "1X2",
            "Match Result market (Home/Draw/Away)",
            "Three-way market; draws occur 25-30% in group stage but public undervalues them",
        ),
        (
            "Over/Under 2.5",
            "Total goals market above or below 2.5",
            "Group stage overs ~50-55%; knockout unders ~55-60%; semifinals lowest-scoring historically",
        ),
        (
            "Correct Score",
            "Exact final score betting",
            "25-35% house edge; entertainment-only or specific tactical locks",
        ),
        (
            "Futures",
            "Long-term tournament outcome bets",
            "Pre-tournament value hunting; path analysis critical; wide spreads and information risk",
        ),
        (
            "Team Props",
            "Team-specific markets (corners, cards, clean sheets)",
            "Less public attention than match winners; tactical system predictability creates edges",
        ),
        (
            "Soft Qualification",
            "66.7% of teams advance (32 of 48)",
            "Reduces elimination pressure; alters tactical incentives in Matchday 2-3",
        ),
        (
            "Rotation Risk",
            "Star players rested after securing advancement",
            "Systematic value on underdogs/unders when Tier 1 teams rest starters in Matchday 3",
        ),
        (
            "Environmental Edge",
            "Altitude/heat/humidity/travel impact on performance",
            "Mexico City altitude (2,240m), Miami humidity create venue-specific baselines ignored by aggregate models",
        ),
        (
            "Narrative Inflation",
            "Public money distortion on popular players/teams",
            "Messi farewell, host nations, Ronaldo-effect create prices 10-15% shorter than true probability",
        ),
        (
            "Line Shopping",
            "Comparing odds across multiple bookmakers",
            "Lowest-complexity, highest-return improvement; 5% edge across 50 wagers = significant cumulative impact",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO betting_glossary (term, definition, wc2026_relevance)
        VALUES (?, ?, ?)
    """
    execute_many(query, terms, db_path)
    print(f"  -> {len(terms)} glossary terms seeded")


def seed_key_dates(db_path: str = None):
    """Seed the key dates timeline."""
    dates = [
        (
            "~May 20–25, 2026",
            "Squad announcements (estimated window)",
            "Information shock—evaluate futures positions; adjust group stage targets",
            "critical",
        ),
        (
            "June 11, 2026",
            "Opening match (Estadio Azteca, Mexico City)",
            "Observe altitude effects; calibrate totals baseline for Mexico City",
            "critical",
        ),
        (
            "June 15–17, 2026",
            "Matchday 1 completion",
            "Assess tactical patterns; identify overperforming/underperforming teams",
            "high",
        ),
        (
            "June 18–21, 2026",
            "Matchday 2",
            "Must-win dynamics emerge; rotation indicators visible",
            "high",
        ),
        (
            "June 24–27, 2026",
            "Matchday 3",
            "Highest group-stage value—simultaneous kickoffs, qualification scenarios",
            "critical",
        ),
        (
            "June 28–July 3, 2026",
            "Round of 32",
            "New stage inefficiencies; bracket path crystallization",
            "critical",
        ),
        (
            "July 4–7, 2026",
            "Round of 16",
            "Knockout dynamics fully active; fatigue assessment critical",
            "high",
        ),
        (
            "July 9–11, 2026",
            "Quarterfinals",
            "Quality concentration; tactical clarity peaks",
            "high",
        ),
        (
            "July 14–15, 2026",
            "Semifinals",
            "Historical lowest-scoring round; contrarian under value",
            "high",
        ),
        (
            "July 19, 2026",
            "Final (MetLife Stadium)",
            "Maximum public money; hedging execution for futures holders",
            "critical",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO key_dates (date_range, event_name, betting_action, priority)
        VALUES (?, ?, ?, ?)
    """
    execute_many(query, dates, db_path)
    print(f"  -> {len(dates)} key dates seeded")


def seed_checklist(db_path: str = None):
    """Seed the pre-tournament checklist."""
    items = [
        (
            "Account Setup",
            "Establish verified accounts with licensed operators (FanDuel, BetMGM, DraftKings minimum)",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Account Setup",
            "Deposit funds across accounts; verify withdrawal methods and timelines",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Account Setup",
            "Set pre-tournament limits: deposit limits, time restrictions, cooling-off triggers",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Account Setup",
            "Configure multi-factor authentication and verify geolocation functionality",
            0,
            "high",
            "2026-06-01",
        ),
        (
            "Information Infrastructure",
            "Curate information sources to 3–4 trusted outlets",
            0,
            "high",
            "2026-06-01",
        ),
        (
            "Information Infrastructure",
            "Subscribe to injury trackers (PhysioRoom, national federation sites)",
            0,
            "high",
            "2026-06-01",
        ),
        (
            "Information Infrastructure",
            "Bookmark statistical platforms: Opta, FBref, Understat",
            0,
            "normal",
            "2026-06-01",
        ),
        (
            "Information Infrastructure",
            "Set up squad announcement alerts (major information shock window)",
            0,
            "critical",
            "2026-05-20",
        ),
        (
            "Information Infrastructure",
            "Study environmental factor matrix for all 16 venues",
            0,
            "high",
            "2026-06-01",
        ),
        (
            "Information Infrastructure",
            "Identify penalty takers for all Tier 1–2 teams and major dark horses",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Strategic Preparation",
            "Establish total tournament bankroll (funds you can afford to lose entirely)",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Strategic Preparation",
            "Allocate bankroll by phase using 40/15/10/10/25 framework",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Strategic Preparation",
            "Define daily exposure caps and weekly loss limits in writing",
            0,
            "critical",
            "2026-06-01",
        ),
        (
            "Strategic Preparation",
            "Pre-identify 5–10 futures positions for early entry before squad announcements",
            0,
            "high",
            "2026-05-15",
        ),
        (
            "Strategic Preparation",
            "Create scenario playbook for Matchday 3 qualification dynamics",
            0,
            "high",
            "2026-06-01",
        ),
        (
            "Strategic Preparation",
            "Identify accountability partner for tilt prevention",
            0,
            "high",
            "2026-06-01",
        ),
        (
            "Jurisdictional Awareness",
            "Verify state/province-specific market availability for World Cup wagering",
            0,
            "normal",
            "2026-06-01",
        ),
        (
            "Jurisdictional Awareness",
            "Understand geolocation restrictions if traveling to host cities",
            0,
            "normal",
            "2026-06-01",
        ),
        (
            "Jurisdictional Awareness",
            "Confirm tax treatment in your primary jurisdiction",
            0,
            "normal",
            "2026-06-01",
        ),
        (
            "Jurisdictional Awareness",
            "Review regulated operator options in Mexico if attending matches there",
            0,
            "normal",
            "2026-06-01",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO checklist_items (category, item, completed, priority, due_by)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_many(query, items, db_path)
    print(f"  -> {len(items)} checklist items seeded")


def seed_betting_scenarios(db_path: str = None):
    """Seed live betting scenarios from the Field Guide."""
    scenarios = [
        (
            "Matchday 3 — Qualification Threshold Crystallization",
            "Group Stage",
            "60th minute: Team A learns 0-0 draw advances them as third-place team. Opponent needs win.",
            "Pre-match odds still reflect must-win pricing for Team A",
            "Back Team B or draw at inflated odds; bet under totals as Team A parks the bus",
            "high",
        ),
        (
            "Altitude/Heat Fatigue — Second Half Collapse",
            "Live",
            "Halftime in Miami/Mexico City: favorite leads 1-0 but expended maximum pressing energy. Underdog defended deep.",
            "Live handicap lines favor favorite continuing dominance",
            "Back underdog second-half goal markets or under total; physical degradation accelerates after 60th minute",
            "high",
        ),
        (
            "Rotation Revelation — Matchday 3 Lineup Release",
            "Group Stage",
            "Tier 1 team resting 6 starters after securing group winner status. Opponent needs result to qualify.",
            "Pre-match AH still prices favorite as full strength",
            "Immediate position on underdog +1 or +1.5 before market adjusts; bet under totals as rotated squads lack cohesion",
            "high",
        ),
        (
            "Knockout Extra Time Transition",
            "Knockout",
            "Knockout match tied 0-0 at 75 minutes. Both teams cautious, substituting defensive players.",
            "Live totals markets may still price late goals based on group-stage scoring rates",
            "Back under 0.5 or 1.5 remaining goals; bet on penalty shootout yes markets if available",
            "medium",
        ),
        (
            "First Half Caution",
            "Live",
            "Matchday 1 opening fixtures: tactical feeling-out process with conservative approaches",
            "Markets may price first-half goals based on season averages",
            "Unders value in first-half markets; card markets for tactical fouls during feeling-out",
            "medium",
        ),
        (
            "Late Match Desperation",
            "Live",
            "75+ minutes: desperation attacking, defensive organization breakdown",
            "Totals markets may not fully price late goal probability",
            "Goal markets, card accumulation, corner overs in final 15 minutes",
            "medium",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO betting_scenarios
        (scenario_name, phase, trigger, market_behavior, recommended_action, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    execute_many(query, scenarios, db_path)
    print(f"  -> {len(scenarios)} betting scenarios seeded")


def seed_environmental_impacts(db_path: str = None):
    """Seed the environmental impact matrix."""
    impacts = [
        (
            "Altitude (2,240m)",
            "Mexico City (Estadio Azteca)",
            "Reduced aerobic capacity; slower tempo; compressed scoring",
            "Under totals; reduced favorite margin",
        ),
        (
            "High humidity + heat",
            "Miami, Houston",
            "Accelerated fatigue; reduced pressing intensity; increased cramping",
            "Under totals; late-match goal suppression",
        ),
        (
            "Arid heat",
            "Dallas, Phoenix (if selected)",
            "Different physiological stress; rapid dehydration",
            "Moderate under tendency; player minute reduction",
        ),
        (
            "Temperate maritime",
            "Seattle, Vancouver",
            "Sustained high intensity; favorable for technical play",
            "Standard totals; technical team advantage",
        ),
        (
            "Variable continental",
            "Toronto, Boston, New York",
            "Weather unpredictability; potential precipitation",
            "Totals volatility; surface condition uncertainty",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO environmental_impacts
        (factor, affected_venues, performance_impact, betting_market_implication)
        VALUES (?, ?, ?, ?)
    """
    execute_many(query, impacts, db_path)
    print(f"  -> {len(impacts)} environmental impacts seeded")


def seed_bankroll_phases(db_path: str = None):
    """Seed bankroll phase allocation framework."""
    phases = [
        (
            "Group Stage",
            "1-14",
            40,
            "5-8% of remaining bankroll",
            "Information gathering, tactical identification",
        ),
        (
            "Round of 32",
            "15-18",
            15,
            "8-10% of remaining bankroll",
            "Bracket path analysis, fatigue assessment",
        ),
        (
            "Round of 16",
            "19-21",
            10,
            "10-12% of remaining bankroll",
            "Knockout dynamics, elimination pressure",
        ),
        (
            "Quarterfinals",
            "22-24",
            10,
            "12-15% of remaining bankroll",
            "Quality concentration, tactical clarity",
        ),
        (
            "Semifinals & Final",
            "25-39",
            25,
            "15-20% of remaining bankroll",
            "High-leverage opportunities, information advantage",
        ),
    ]

    query = """
        INSERT OR REPLACE INTO bankroll_phases
        (phase, days, allocation_pct, daily_exposure_limit, strategic_focus)
        VALUES (?, ?, ?, ?, ?)
    """
    execute_many(query, phases, db_path)
    print(f"  -> {len(phases)} bankroll phases seeded")


def seed_set_piece_specialists(db_path: str = None):
    """Seed set-piece specialists from major teams."""
    specialists = [
        (
            "Trent Alexander-Arnold",
            "England",
            0,
            1,
            0,
            1,
            0,
            "Elite delivery from corners and free kicks",
        ),
        (
            "Kieran Trippier",
            "England",
            0,
            1,
            0,
            1,
            0,
            "Set-piece specialist; dangerous delivery",
        ),
        (
            "Bruno Fernandes",
            "Portugal",
            0,
            1,
            1,
            0,
            1,
            "Corners, free kicks, and penalties",
        ),
        ("Lionel Messi", "Argentina", 1, 1, 0, 0, 0, "Penalties and free kicks"),
        ("Kylian Mbappé", "France", 1, 0, 1, 0, 0, "Penalties and direct free kicks"),
        (
            "Antoine Griezmann",
            "France",
            0,
            1,
            1,
            0,
            1,
            "Corners and indirect free kicks",
        ),
        ("Toni Kroos", "Germany", 0, 1, 1, 0, 0, "Elite free kick delivery"),
        ("Marco Asensio", "Spain", 0, 1, 1, 0, 0, "Direct free kick threat"),
        (
            "Christian Pulisic",
            "United States",
            1,
            0,
            1,
            0,
            0,
            "Penalties and set pieces",
        ),
        ("Luka Modrić", "Croatia", 0, 1, 1, 0, 0, "Indirect free kicks and corners"),
    ]

    query = """
        INSERT OR REPLACE INTO set_piece_specialists
        (player_name, team_name, penalty_taker, primary_free_kick, secondary_free_kick, primary_corner, secondary_corner, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_many(query, specialists, db_path)
    print(f"  -> {len(specialists)} set-piece specialists seeded")


def run_all_seeds(db_path: str = None):
    """Run all Field Guide reference data seeding."""
    print("\n=== Smart Bet Field Guide — Reference Data Seeding ===\n")
    create_reference_tables(db_path)
    print()
    seed_team_tiers(db_path)
    seed_penalty_takers(db_path)
    seed_set_piece_specialists(db_path)
    seed_betting_glossary(db_path)
    seed_key_dates(db_path)
    seed_checklist(db_path)
    seed_betting_scenarios(db_path)
    seed_environmental_impacts(db_path)
    seed_bankroll_phases(db_path)
    print("\n=== Seeding Complete ===")


if __name__ == "__main__":
    run_all_seeds()
