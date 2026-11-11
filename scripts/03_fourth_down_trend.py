"""The fourth-down revolution: how often teams go for it, by season.

Share of fourth downs where the offense ran a play instead of punting or
kicking, split by distance to go. Limited to competitive game states (win
probability 20-80%) so desperation attempts don't inflate the rate.
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser, in_progress_note
from nflstats.plotting import INK_2, SERIES, apply_style, finish, titles

args = base_parser(__doc__, start=2000).parse_args()

columns = ["season", "season_type", "down", "ydstogo", "play_type", "wp"]
pbp = regular_season(load_pbp(range(args.start, args.end + 1), columns=columns))
fourth = pbp[
    (pbp["down"] == 4)
    & pbp["play_type"].isin(["pass", "run", "punt", "field_goal"])
    & pbp["wp"].between(0.2, 0.8)
].copy()
fourth["went"] = fourth["play_type"].isin(["pass", "run"])
fourth["distance"] = pd.cut(fourth["ydstogo"], [0, 2, 5, 99], labels=["4th & 1-2", "4th & 3-5", "4th & 6+"])
rates = fourth.groupby(["season", "distance"], observed=True)["went"].mean().unstack()

apply_style()
fig, ax = plt.subplots()
for color, distance in zip(SERIES, rates.columns):
    ax.plot(rates.index, rates[distance], color=color, label=distance)
    last = rates[distance].iloc[-1]
    ax.annotate(f"{distance}  {last:.0%}", (rates.index[-1], last), xytext=(8, 0),
                textcoords="offset points", va="center", fontsize=9.5, color=INK_2)
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_ylim(0, None)
ax.set_xlim(args.start - 0.5, args.end + (args.end - args.start) * 0.16)
ax.set_xticks([s for s in rates.index if s % 5 == 0])
ax.grid(axis="x", visible=False)
ax.set_ylabel("Go-for-it rate")
ax.legend(loc="upper left")
titles(ax, "The fourth-down revolution",
       f"Share of fourth downs where the offense went for it, {args.start}-{args.end}. Win probability 20-80% only.{in_progress_note(args.end)}")
finish(fig, f"03_fourth_down_trend_{args.start}_{args.end}", args.show)
