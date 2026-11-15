"""Scoring environment: points per game against the betting total.

Average combined points per game each season next to the average closing
over/under. The gap shows where the market was caught out: seasons where
scoring ran ahead of the totals (2020's empty stadiums) and seasons where
it fell short.
"""

import matplotlib.pyplot as plt

from nflstats import load_schedules, regular_season
from nflstats.cli import base_parser, in_progress_note
from nflstats.plotting import INK_2, MUTED, SERIES, apply_style, finish, titles

args = base_parser(__doc__, start=1999).parse_args()

games = regular_season(load_schedules(range(args.start, args.end + 1)))
games = games[games["total"].notna() & games["total_line"].notna()]
seasons = games.groupby("season").agg(points=("total", "mean"), line=("total_line", "mean"),
                                      over_rate=("total", lambda t: (t > games.loc[t.index, "total_line"]).mean()))
seasons["gap"] = seasons["points"] - seasons["line"]
print(seasons.round(2).to_string())

apply_style()
fig, ax = plt.subplots()
ax.fill_between(seasons.index, seasons["points"], seasons["line"], color=SERIES[0], alpha=0.12, linewidth=0)
ax.plot(seasons.index, seasons["line"], color=MUTED, linestyle=(0, (4, 3)), label="Closing over/under")
ax.plot(seasons.index, seasons["points"], color=SERIES[0], marker="o", markersize=4.5, label="Actual points")
for season in (seasons["gap"].idxmax(), seasons["gap"].idxmin()):
    gap, points = seasons.loc[season, "gap"], seasons.loc[season, "points"]
    ax.annotate(f"{season}: {gap:+.1f} vs line", (season, points), xytext=(-7, 7) if gap > 0 else (0, -14),
                textcoords="offset points", ha="right" if gap > 0 else "center", va="center", fontsize=9,
                color=INK_2)
last = seasons.iloc[-1]
ax.annotate(f"{last['points']:.1f}", (seasons.index[-1], last["points"]), xytext=(8, 0),
            textcoords="offset points", va="center", fontsize=9.5, color=INK_2)
ax.set_xlim(args.start - 0.5, args.end + (args.end - args.start) * 0.07)
ax.set_xticks([s for s in seasons.index if s % 5 == 0])
ax.margins(y=0.15)
ax.grid(axis="x", visible=False)
ax.set_ylabel("Combined points per game")
ax.legend(loc="upper left")
titles(ax, "Scoring against the betting total",
       f"Average combined points per game and average closing over/under, regular season, {args.start}-{args.end}."
       f"{in_progress_note(args.end)}")
finish(fig, f"17_scoring_vs_totals_{args.start}_{args.end}", args.show)
