"""Fast starters and closers: scoring margin by quarter.

Average points scored minus points allowed in each quarter, per game, for
every team. Shows who jumps on opponents early, who fades after halftime
and who wins the fourth quarter. Overtime is left out.
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import INK, NEGATIVE, POSITIVE, SURFACE, apply_style, finish, titles

args = base_parser(__doc__).parse_args()

columns = ["season_type", "game_id", "home_team", "away_team", "qtr", "total_home_score", "total_away_score"]
pbp = regular_season(load_pbp(args.season, columns=columns))
pbp = pbp[pbp["qtr"] <= 4]

# Running score at the end of each quarter, differenced into points scored within the quarter.
keys = ["game_id", "home_team", "away_team"]
running = pbp.groupby(keys + ["qtr"])[["total_home_score", "total_away_score"]].max()
scored = running.groupby(level="game_id").diff().fillna(running).reset_index()
scored["home_margin"] = scored["total_home_score"] - scored["total_away_score"]
by_team = pd.concat([
    pd.DataFrame({"team": scored["home_team"], "qtr": scored["qtr"], "margin": scored["home_margin"]}),
    pd.DataFrame({"team": scored["away_team"], "qtr": scored["qtr"], "margin": -scored["home_margin"]}),
])

grid = by_team.groupby(["team", "qtr"])["margin"].mean().unstack()
grid.columns = [f"Q{int(q)}" for q in grid.columns]
grid = grid.loc[grid.sum(axis=1).sort_values(ascending=False).index]
print(grid.assign(total=grid.sum(axis=1)).round(2).to_string())

apply_style()
fig, ax = plt.subplots(figsize=(8, 11))
limit = grid.abs().max().max()
cmap = LinearSegmentedColormap.from_list("margin", [NEGATIVE, SURFACE, POSITIVE])
ax.imshow(grid, cmap=cmap, norm=TwoSlopeNorm(0, -limit, limit), aspect="auto")
for row, team in enumerate(grid.index):
    for col, value in enumerate(grid.loc[team]):
        ax.text(col, row, f"{value:+.1f}", ha="center", va="center", fontsize=9,
                color=SURFACE if abs(value) > limit * 0.7 else INK)
ax.set_xticks(range(len(grid.columns)), grid.columns)
ax.set_yticks(range(len(grid.index)), grid.index)
ax.grid(visible=False)
for spine in ax.spines.values():
    spine.set_visible(False)
# White gaps between cells.
ax.set_xticks([x - 0.5 for x in range(1, len(grid.columns))], minor=True)
ax.set_yticks([y - 0.5 for y in range(1, len(grid.index))], minor=True)
ax.grid(which="minor", color=SURFACE, linewidth=2)
ax.tick_params(which="minor", length=0)
titles(ax, f"Fast starters and closers, {args.season}",
       "Average scoring margin per game in each quarter, regular season. Sorted by total; overtime excluded.")
finish(fig, f"15_quarter_margins_{args.season}", args.show)
