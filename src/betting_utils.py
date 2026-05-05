"""
Smart Bet Field Guide System 2026 — Betting Utilities
Odds conversion, bankroll calculations, implied probability,
and Kelly Criterion sizing.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Odds:
    """Represents betting odds in multiple formats."""

    decimal: float = 0.0
    american: int = 0
    fractional_num: int = 0
    fractional_den: int = 0
    implied_prob: float = 0.0

    def __str__(self) -> str:
        if self.decimal > 0:
            return f"Decimal: {self.decimal:.2f} | American: {self.american:+d} | Implied: {self.implied_prob:.1%}"
        return "Invalid odds"


def decimal_to_american(decimal: float) -> int:
    """Convert decimal odds to American odds."""
    if decimal >= 2.0:
        return int((decimal - 1) * 100)
    else:
        return int(-100 / (decimal - 1))


def american_to_decimal(american: int) -> float:
    """Convert American odds to decimal odds."""
    if american > 0:
        return (american / 100.0) + 1.0
    else:
        return (100.0 / abs(american)) + 1.0


def decimal_to_fractional(decimal: float) -> Tuple[int, int]:
    """Convert decimal odds to fractional odds (num, den)."""
    profit = decimal - 1.0
    # Simple approximation
    if profit >= 1.0:
        return int(profit * 100), 100
    else:
        return 100, int(100 / profit)


def american_to_implied_prob(american: int) -> float:
    """Convert American odds to implied probability."""
    if american > 0:
        return 100.0 / (american + 100.0)
    else:
        return abs(american) / (abs(american) + 100.0)


def decimal_to_implied_prob(decimal: float) -> float:
    """Convert decimal odds to implied probability."""
    if decimal <= 0:
        return 0.0
    return 1.0 / decimal


def parse_odds(value: str) -> Odds:
    """Parse an odds string and return all formats."""
    value = value.strip()

    # Try American first (+150, -250) to avoid misinterpreting as decimal
    if value.startswith("+") or value.startswith("-"):
        try:
            am = int(value)
            if am != 0:
                dec = american_to_decimal(am)
                prob = american_to_implied_prob(am)
                num, den = decimal_to_fractional(dec)
                return Odds(
                    decimal=dec,
                    american=am,
                    fractional_num=num,
                    fractional_den=den,
                    implied_prob=prob,
                )
        except ValueError:
            pass

    # Try decimal
    try:
        dec = float(value)
        if dec > 1.0:
            am = decimal_to_american(dec)
            prob = decimal_to_implied_prob(dec)
            num, den = decimal_to_fractional(dec)
            return Odds(
                decimal=dec,
                american=am,
                fractional_num=num,
                fractional_den=den,
                implied_prob=prob,
            )
    except ValueError:
        pass

    # Try fractional (6/4)
    if "/" in value:
        try:
            parts = value.split("/")
            num = int(parts[0])
            den = int(parts[1])
            dec = (num / den) + 1.0
            am = decimal_to_american(dec)
            prob = decimal_to_implied_prob(dec)
            return Odds(
                decimal=dec,
                american=am,
                fractional_num=num,
                fractional_den=den,
                implied_prob=prob,
            )
        except (ValueError, ZeroDivisionError):
            pass

    return Odds()


def kelly_criterion(
    model_prob: float, odds_decimal: float, fraction: float = 0.25
) -> Tuple[float, str]:
    """
    Calculate Kelly Criterion bet sizing.

    Args:
        model_prob: Your estimated probability of winning (0-1)
        odds_decimal: Decimal odds offered
        fraction: Kelly fraction (0.25 = quarter Kelly, safer)

    Returns:
        (stake_pct, recommendation)
    """
    if model_prob <= 0 or odds_decimal <= 1.0:
        return 0.0, "Invalid input"

    edge = (model_prob * odds_decimal) - 1.0
    if edge <= 0:
        return 0.0, "No edge—do not bet"

    full_kelly = edge / (odds_decimal - 1.0)
    stake = full_kelly * fraction

    stake = min(stake, 0.05)  # Cap at 5% of bankroll

    if stake >= 0.03:
        rec = f"Strong edge—bet {stake:.2%} of bankroll ({fraction:.0%} Kelly)"
    elif stake >= 0.01:
        rec = f"Moderate edge—bet {stake:.2%} of bankroll ({fraction:.0%} Kelly)"
    else:
        rec = f"Weak edge—bet {stake:.2%} of bankroll or pass"

    return stake, rec


def clv_analysis(entry_odds: float, closing_odds: float) -> Tuple[float, str]:
    """
    Calculate Closing Line Value (CLV).

    Positive CLV = you beat the closing line (good sign)
    """
    if closing_odds <= 1.0 or entry_odds <= 1.0:
        return 0.0, "Invalid odds"

    # For favorites (odds < 2.0), closing toward lower number = good
    # For underdogs (odds > 2.0), closing toward higher number = good

    entry_prob = 1.0 / entry_odds
    closing_prob = 1.0 / closing_odds

    clv = entry_prob - closing_prob

    if clv > 0.02:
        return clv, "Excellent CLV—strong sharp indicator"
    elif clv > 0.01:
        return clv, "Good CLV—likely +EV"
    elif clv > 0:
        return clv, "Slight CLV—marginal edge"
    else:
        return clv, "Negative CLV—market moved against you"


def bankroll_allocation(
    phase: str, total_bankroll: float, remaining_bankroll: float
) -> dict:
    """Get recommended allocation for a tournament phase."""
    from database import get_connection

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM bankroll_phases WHERE phase = ?", (phase,)
        ).fetchone()

    if not row:
        return {"error": f"Phase '{phase}' not found"}

    alloc_pct = row["allocation_pct"]
    phase_alloc = total_bankroll * (alloc_pct / 100.0)

    return {
        "phase": phase,
        "total_bankroll": total_bankroll,
        "remaining_bankroll": remaining_bankroll,
        "phase_allocation_pct": alloc_pct,
        "phase_allocation_amount": phase_alloc,
        "daily_exposure_limit": row["daily_exposure_limit"],
        "strategic_focus": row["strategic_focus"],
        "recommended_single_bet_max": remaining_bankroll * 0.03,
        "recommended_single_bet_exceptional": remaining_bankroll * 0.05,
    }


def calculate_ev(model_prob: float, odds_decimal: float) -> Tuple[float, str]:
    """Calculate expected value of a bet."""
    ev = (model_prob * (odds_decimal - 1.0)) - (1.0 - model_prob)

    if ev > 0.05:
        return ev, "Strong +EV"
    elif ev > 0.02:
        return ev, "Moderate +EV"
    elif ev > 0:
        return ev, "Marginal +EV"
    else:
        return ev, "-EV or fair—do not bet"


if __name__ == "__main__":
    # Demo
    print("=== Odds Conversion Demo ===")
    for val in ["2.50", "+150", "6/4", "-250"]:
        odds = parse_odds(val)
        print(f"  {val:>6s} -> {odds}")

    print("\n=== Kelly Criterion Demo ===")
    stake, rec = kelly_criterion(0.45, 2.50)
    print(f"  Model prob 45%, odds 2.50: {rec}")

    print("\n=== CLV Analysis Demo ===")
    clv, rec = clv_analysis(2.20, 2.00)
    print(f"  Entry 2.20, close 2.00: CLV = {clv:.2%}, {rec}")

    print("\n=== EV Calculation Demo ===")
    ev, rec = calculate_ev(0.42, 2.50)
    print(f"  Model prob 42%, odds 2.50: EV = {ev:.2%}, {rec}")
