"""Cached loaders for nflverse data (via nflreadpy), returned as pandas DataFrames.

Downloads land as parquet files in ``data/`` at the repo root, so each
season is only fetched once. The in-progress season is re-fetched when its
cached copy is more than ``STALE_HOURS`` old.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path

import nflreadpy as nfl
import pandas as pd
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
STALE_HOURS = 12


def current_season() -> int:
    """The most recent season with games played."""
    return nfl.get_current_season()


def _is_stale(path: Path) -> bool:
    return (time.time() - path.stat().st_mtime) > STALE_HOURS * 3600


def _cached(
    name: str,
    fetch: Callable[[], pl.DataFrame],
    columns: Sequence[str] | None = None,
    live: bool = False,
    refresh: bool = False,
) -> pd.DataFrame:
    """Read ``data/<name>.parquet``, downloading it first when needed.

    ``live`` marks data that still changes (the current season), which is
    re-downloaded once stale.
    """
    path = DATA_DIR / f"{name}.parquet"
    if refresh or not path.exists() or (live and _is_stale(path)):
        DATA_DIR.mkdir(exist_ok=True)
        print(f"downloading {name} ...")
        fetch().write_parquet(path)
    return pd.read_parquet(path, columns=list(columns) if columns else None)


def _as_seasons(seasons: int | Iterable[int] | None) -> list[int]:
    if seasons is None:
        return [current_season()]
    if isinstance(seasons, int):
        return [seasons]
    return sorted(seasons)


def load_pbp(
    seasons: int | Iterable[int] | None = None,
    columns: Sequence[str] | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """Play-by-play for one or more seasons (default: the current season).

    Pass ``columns`` when loading many seasons - the full table has ~370
    columns and ~50k rows per season.
    """
    now = current_season()
    frames = [
        _cached(
            f"pbp_{season}",
            lambda season=season: nfl.load_pbp([season]),
            columns=columns,
            live=season >= now,
            refresh=refresh,
        )
        for season in _as_seasons(seasons)
    ]
    return pd.concat(frames, ignore_index=True)


def load_schedules(
    seasons: int | Iterable[int] | None = None, refresh: bool = False
) -> pd.DataFrame:
    """Games with scores and betting lines. ``seasons=None`` returns every season since 1999."""
    games = _cached("schedules", lambda: nfl.load_schedules(True), live=True, refresh=refresh)
    if seasons is not None:
        games = games[games["season"].isin(_as_seasons(seasons))]
    return games.reset_index(drop=True)


def load_teams(refresh: bool = False) -> pd.DataFrame:
    """Team names, divisions and colors."""
    return _cached("teams", nfl.load_teams, refresh=refresh)


def load_players(refresh: bool = False) -> pd.DataFrame:
    """Player directory (ids, names, positions)."""
    return _cached("players", nfl.load_players, live=True, refresh=refresh)


def regular_season(df: pd.DataFrame) -> pd.DataFrame:
    """Keep regular-season rows of a play-by-play or schedule table."""
    column = "season_type" if "season_type" in df.columns else "game_type"
    return df[df[column] == "REG"]


def scrimmage_plays(pbp: pd.DataFrame) -> pd.DataFrame:
    """Regular-season runs and dropbacks with an EPA value.

    This is the standard filter for efficiency stats: it drops kicks,
    kneels, spikes, penalties without a play, and timeouts.
    """
    plays = regular_season(pbp)
    keep = ((plays["pass"] == 1) | (plays["rush"] == 1)) & plays["epa"].notna()
    return plays[keep & plays["posteam"].notna()]
