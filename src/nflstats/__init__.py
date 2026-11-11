"""Workspace helpers for exploring NFL data: cached loaders and a shared plot style."""

from nflstats.data import (
    current_season,
    load_pbp,
    load_players,
    load_schedules,
    load_teams,
    regular_season,
    scrimmage_plays,
)

__all__ = [
    "current_season",
    "load_pbp",
    "load_players",
    "load_schedules",
    "load_teams",
    "regular_season",
    "scrimmage_plays",
]
