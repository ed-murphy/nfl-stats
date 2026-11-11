# nflstats

A workspace for generating NFL stats and plots from [nflverse](https://github.com/nflverse) data
(play-by-play back to 1999, schedules, betting lines, rosters) via
[nflreadpy](https://github.com/nflverse/nflreadpy).

## Setup

Requires [uv](https://docs.astral.sh/uv/). From the repo root:

```bash
uv sync
```

## Run a script

```bash
uv run scripts/01_team_tiers.py
```

Each script saves a PNG to `plots/`. Common options:

| Option | Meaning |
|---|---|
| `--season 2025` | season to analyse (single-season scripts; default is the current season) |
| `--start 2010 --end 2025` | season range (trend scripts) |
| `--show` | also open the plot in a window |
| `--help` | what the stat is, plus any script-specific options |

## The scripts

| Script | Stat | Extra options |
|---|---|---|
| `01_team_tiers.py` | Offense vs defense EPA per play for every team | |
| `02_qb_efficiency.py` | QB EPA per dropback vs completion % over expected | `--min-per-week` |
| `03_fourth_down_trend.py` | Fourth-down go-for-it rate by season and distance | |
| `04_field_goal_range.py` | Field goal make rate by distance, across three eras | `--min-kicks` |
| `05_pass_rate_over_expected.py` | Which teams pass more than the situation predicts | |
| `06_wildest_game.py` | Win-probability chart of the season's most volatile game | `--game-id` |
| `07_receiver_usage.py` | Target share vs air-yards share for top receivers | `--top` |
| `08_home_field_advantage.py` | Average home scoring margin by season | `--window` |
| `09_pythagorean_luck.py` | Actual wins vs wins expected from points for/against | |
| `10_team_season_arc.py` | One team's offense and defense EPA, game by game | `--team` |

## Layout

```
src/nflstats/
  data.py      cached loaders: load_pbp, load_schedules, load_teams, load_players
  plotting.py  shared plot style, colors, and helpers (team scatter, diverging bars, titles)
  cli.py       shared command-line options
scripts/       one script per stat
data/          downloaded parquet files (git-ignored)
plots/         generated PNGs (git-ignored)
```

## Data and caching

The first run of a script downloads what it needs into `data/` (one parquet file per season of
play-by-play). Later runs read from disk. The current season is re-downloaded when its copy is
more than 12 hours old; pass `refresh=True` to any loader to force it. The trend scripts (03, 04)
download every season in their range on first run, about 27 files.

## Adding a stat

Copy the closest existing script. The usual shape is:

```python
import matplotlib.pyplot as plt

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, finish, titles

args = base_parser(__doc__).parse_args()
plays = scrimmage_plays(load_pbp(args.season, columns=["season_type", "posteam", "pass", "rush", "epa"]))
stat = plays.groupby("posteam")["epa"].mean()

apply_style()
fig, ax = plt.subplots()
ax.bar(stat.index, stat)
titles(ax, "My stat", "What it measures")
finish(fig, f"11_my_stat_{args.season}", args.show)
```

`scrimmage_plays` keeps regular-season runs and dropbacks that have an EPA value. Pass `columns=`
to `load_pbp` when loading several seasons, since the full table has about 370 columns. Column
definitions are in the [nflfastR field descriptions](https://www.nflfastr.com/articles/field_descriptions.html).
