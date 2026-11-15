"""The death and rebirth of the kickoff return.

Share of kickoffs that were actually returned, by season. Rule changes
aimed at safety pushed the rate down for a decade; the 2024 "dynamic
kickoff" and the 2025 move of the touchback to the 35 were designed to
bring the return back.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser, in_progress_note
from nflstats.plotting import AXIS, INK_2, SERIES, apply_style, finish, titles

RULE_CHANGES = {
    2011: "Kickoff moved\nup to the 35",
    2016: "Touchback\nto the 25",
    2024: "Dynamic\nkickoff",
}

args = base_parser(__doc__, start=2000).parse_args()

columns = ["season", "season_type", "play_type", "touchback", "kickoff_returner_player_id", "return_yards"]
pbp = regular_season(load_pbp(range(args.start, args.end + 1), columns=columns))
kicks = pbp[pbp["play_type"] == "kickoff"].copy()
kicks["returned"] = kicks["kickoff_returner_player_id"].notna() & (kicks["touchback"] != 1)
seasons = kicks.groupby("season").agg(kickoffs=("returned", "size"), return_rate=("returned", "mean"),
                                      touchback_rate=("touchback", "mean"))
seasons["yards_per_return"] = kicks[kicks["returned"]].groupby("season")["return_yards"].mean()
print(seasons.round(3).to_string())

apply_style()
fig, ax = plt.subplots()
ax.plot(seasons.index, seasons["return_rate"], color=SERIES[0], marker="o", markersize=4.5)
for season, label in RULE_CHANGES.items():
    if season in seasons.index:
        ax.axvline(season - 0.5, color=AXIS, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(season - 0.3, 0.03, label, fontsize=9, color=INK_2, va="bottom", linespacing=1.4)
last = seasons["return_rate"].iloc[-1]
ax.annotate(f"{last:.0%}", (seasons.index[-1], last), xytext=(8, 0), textcoords="offset points",
            va="center", fontsize=9.5, color=INK_2)
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_ylim(0, 1)
ax.set_xlim(args.start - 0.5, args.end + (args.end - args.start) * 0.07)
ax.set_xticks([s for s in seasons.index if s % 5 == 0])
ax.grid(axis="x", visible=False)
ax.set_ylabel("Share of kickoffs returned")
titles(ax, "The death and rebirth of the kickoff return",
       f"Share of kickoffs that were returned, regular season, {args.start}-{args.end}.{in_progress_note(args.end)}")
finish(fig, f"13_kickoff_returns_{args.start}_{args.end}", args.show)
