"""Kickers keep getting better: field goal make rate by distance and era.

Splits the season range into three equal eras and plots how often kicks
were made from each distance. The gap between eras is widest on long kicks.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp
from nflstats.cli import base_parser
from nflstats.plotting import INK_2, ORDINAL, apply_style, finish, titles

parser = base_parser(__doc__, start=2000)
parser.add_argument("--min-kicks", type=int, default=25, help="hide distance bins with fewer kicks (default 25)")
args = parser.parse_args()

columns = ["season", "play_type", "field_goal_result", "kick_distance"]
pbp = load_pbp(range(args.start, args.end + 1), columns=columns)
kicks = pbp[(pbp["play_type"] == "field_goal") & pbp["kick_distance"].notna()].copy()
kicks["made"] = kicks["field_goal_result"] == "made"

# Three eras of (nearly) equal length.
edges = np.linspace(args.start, args.end + 1, 4).round().astype(int)
era_names = [f"{a}-{b - 1}" for a, b in zip(edges[:-1], edges[1:])]
kicks["era"] = pd.cut(kicks["season"], edges, right=False, labels=era_names)
# 5-yard bins labelled by their midpoint: 20-24 -> 22, 25-29 -> 27, ...
kicks["bin"] = (kicks["kick_distance"] // 5 * 5 + 2).astype(int)

table = kicks.groupby(["bin", "era"], observed=True)["made"].agg(["mean", "size"])
rates = table["mean"].where(table["size"] >= args.min_kicks).unstack().loc[20:].dropna(how="all")

apply_style()
fig, ax = plt.subplots()
for color, era in zip(ORDINAL, rates.columns):
    series = rates[era].dropna()
    ax.plot(series.index, series, color=color, marker="o", label=era)
    # Label the line's end; a line that stops early is labelled on its left to stay clear of the others.
    stops_early = series.index[-1] < rates.index[-1]
    ax.annotate(era, (series.index[-1], series.iloc[-1]), xytext=(-9 if stops_early else 9, -5 if stops_early else 0),
                textcoords="offset points", ha="right" if stops_early else "left", va="center", fontsize=9.5,
                color=INK_2)
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_xticks(rates.index, [f"{b - 2}-{b + 2}" for b in rates.index])
ax.set_xlim(rates.index[0] - 2, rates.index[-1] + 6)
ax.set_ylim(0, 1.02)
ax.grid(axis="x", visible=False)
ax.set_xlabel("Kick distance (yards)")
ax.set_ylabel("Field goals made")
ax.legend(loc="lower left", title="Seasons", alignment="left")
titles(ax, "Kickers keep getting better",
       f"Field goal make rate by distance and era, all games. Bins with fewer than {args.min_kicks} kicks are hidden.")
finish(fig, f"04_field_goal_range_{args.start}_{args.end}", args.show)
