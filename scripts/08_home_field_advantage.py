"""Is home-field advantage disappearing?

Average home-team scoring margin per regular season, with a rolling
average to show the trend through the year-to-year noise. Neutral-site
games are excluded.
"""

import matplotlib.pyplot as plt

from nflstats import load_schedules, regular_season
from nflstats.cli import base_parser, in_progress_note
from nflstats.plotting import AXIS, INK_2, MUTED, SERIES, apply_style, finish, titles

parser = base_parser(__doc__, start=1999)
parser.add_argument("--window", type=int, default=5, help="rolling-average window in seasons (default 5)")
args = parser.parse_args()

games = regular_season(load_schedules(range(args.start, args.end + 1)))
games = games[games["result"].notna() & (games["location"] == "Home")]
margin = games.groupby("season")["result"].mean()
rolling = margin.rolling(args.window, min_periods=args.window).mean()

apply_style()
fig, ax = plt.subplots()
ax.axhline(0, color=AXIS, linewidth=1)
ax.scatter(margin.index, margin, s=42, color=MUTED, zorder=3, label="Single season")
ax.plot(rolling.index, rolling, color=SERIES[0], label=f"{args.window}-season average")
if 2020 in margin.index:
    ax.annotate("2020: empty stadiums", (2020, margin[2020]), xytext=(9, 0), textcoords="offset points",
                va="center", fontsize=9, color=INK_2)
ax.set_ylim(min(-0.5, margin.min() - 0.6), margin.max() + 0.6)
ax.grid(axis="x", visible=False)
ax.set_ylabel("Average home margin (points)")
ax.legend(loc="upper right")
titles(ax, "Is home-field advantage disappearing?",
       f"Average home-team scoring margin, regular season, {args.start}-{args.end}. Neutral-site games excluded.{in_progress_note(args.end)}")
finish(fig, f"08_home_field_advantage_{args.start}_{args.end}", args.show)
