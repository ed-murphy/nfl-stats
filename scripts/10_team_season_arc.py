"""One team's season, game by game: offensive and defensive EPA per play.

Shows when a team's units were hot or cold across the season. The defense
line is EPA allowed with the sign flipped, so up is good for both lines.
"""

import matplotlib.pyplot as plt
import numpy as np

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import AXIS, INK_2, SERIES, apply_style, finish, titles

parser = base_parser(__doc__)
parser.add_argument("--team", default="KC", help="team abbreviation (default KC)")
args = parser.parse_args()
team = args.team.upper()

columns = ["season_type", "week", "posteam", "defteam", "home_team", "pass", "rush", "epa"]
plays = scrimmage_plays(load_pbp(args.season, columns=columns))
if team not in set(plays["posteam"]):
    raise SystemExit(f"unknown team {team!r}; choose from: {', '.join(sorted(plays['posteam'].unique()))}")

offense = plays[plays["posteam"] == team].groupby("week").agg(
    epa=("epa", "mean"), opponent=("defteam", "first"), home=("home_team", "first"))
defense = -plays[plays["defteam"] == team].groupby("week")["epa"].mean()
opponents = [opp if home == team else f"@{opp}" for opp, home in zip(offense["opponent"], offense["home"])]

apply_style()
fig, ax = plt.subplots(figsize=(11, 6))
ax.axhline(0, color=AXIS, linewidth=1)
lines = {"Offense": offense["epa"], "Defense": defense}
ends = [series.iloc[-1] for series in lines.values()]
# Nudge the end-of-line labels apart when the two lines finish close together.
nudges = np.where(np.argsort(np.argsort(ends)) == 1, 6, -6) if abs(ends[0] - ends[1]) < 0.05 else [0, 0]
for (label, series), color, nudge in zip(lines.items(), SERIES, nudges):
    ax.plot(series.index, series, color=color, marker="o", label=label)
    ax.annotate(label, (series.index[-1], series.iloc[-1]), xytext=(9, nudge), textcoords="offset points",
                va="center", fontsize=9.5, color=INK_2)
ax.set_xticks(offense.index, [f"Wk {week}\n{opp}" for week, opp in zip(offense.index, opponents)], fontsize=8.5)
ax.set_xlim(offense.index.min() - 0.4, offense.index.max() + 1.1)
low, high = ax.get_ylim()
ax.set_ylim(low, high + (high - low) * 0.12)  # headroom for the legend
ax.grid(axis="x", visible=False)
ax.set_ylabel("EPA per play  (up is better)")
ax.legend(loc="upper left", ncols=2)
titles(ax, f"{team} game by game, {args.season}",
       "EPA per play on offense, and EPA per play allowed on defense with the sign flipped. Zero is league average.")
finish(fig, f"10_team_season_arc_{team}_{args.season}", args.show)
