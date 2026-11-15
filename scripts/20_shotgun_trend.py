"""The shotgun takeover: how offenses line up, by season.

Share of offensive plays run from the shotgun, split into dropbacks and
designed runs, plus the share run without a huddle. Shotgun went from a
passing-down package to the default formation, though under-center looks
have been coming back since 2023.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser, in_progress_note
from nflstats.plotting import INK_2, SERIES, apply_style, finish, titles

args = base_parser(__doc__, start=2006).parse_args()

columns = ["season", "season_type", "posteam", "pass", "rush", "epa", "shotgun", "no_huddle"]
plays = scrimmage_plays(load_pbp(range(args.start, args.end + 1), columns=columns))
rates = plays.groupby("season").agg(no_huddle=("no_huddle", "mean"))
rates.insert(0, "runs", plays[plays["rush"] == 1].groupby("season")["shotgun"].mean())
rates.insert(0, "dropbacks", plays[plays["pass"] == 1].groupby("season")["shotgun"].mean())
print(rates.round(3).to_string())

labels = {"dropbacks": "Shotgun, dropbacks", "runs": "Shotgun, runs", "no_huddle": "No huddle"}

apply_style()
fig, ax = plt.subplots()
for color, (column, label) in zip(SERIES, labels.items()):
    ax.plot(rates.index, rates[column], color=color, label=label)
    last = rates[column].iloc[-1]
    ax.annotate(f"{label}  {last:.0%}", (rates.index[-1], last), xytext=(8, 0),
                textcoords="offset points", va="center", fontsize=9.5, color=INK_2)
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_ylim(0, 1)
ax.set_xlim(args.start - 0.5, args.end + (args.end - args.start) * 0.24)
ax.set_xticks([s for s in rates.index if s % 5 == 0])
ax.grid(axis="x", visible=False)
ax.set_ylabel("Share of plays")
titles(ax, "The shotgun takeover",
       f"Share of dropbacks and runs from shotgun, and of all plays without a huddle, {args.start}-{args.end}."
       f"{in_progress_note(args.end)}")
finish(fig, f"20_shotgun_trend_{args.start}_{args.end}", args.show)
