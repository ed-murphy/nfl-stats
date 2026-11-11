"""Command-line options shared by the scripts in ``scripts/``."""

from __future__ import annotations

import argparse

from nflstats.data import current_season


def base_parser(description: str, season: bool = True, start: int | None = None) -> argparse.ArgumentParser:
    """Parser with ``--show`` plus either ``--season`` or a ``--start``/``--end`` range."""
    parser = argparse.ArgumentParser(description=description)
    if start is not None:
        parser.add_argument("--start", type=int, default=start, help=f"first season (default {start})")
        parser.add_argument("--end", type=int, default=current_season(), help="last season (default: current)")
    elif season:
        parser.add_argument("--season", type=int, default=current_season(), help="season (default: current)")
    parser.add_argument("--show", action="store_true", help="open the plot in a window after saving")
    return parser


def in_progress_note(season: int) -> str:
    """Subtitle suffix flagging that ``season`` is the current, incomplete one."""
    return f" {season} is in progress." if season >= current_season() else ""
