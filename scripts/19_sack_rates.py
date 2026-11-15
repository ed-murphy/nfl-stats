"""Winning the pocket: sack rate for and against.

Share of dropbacks ending in a sack, for each team's defense (sacks made)
and offense (sacks allowed). Teams in the top right get home on defense
while keeping their own quarterback clean.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, corner_notes, finish, mean_lines, team_scatter, titles

args = base_parser(__doc__).parse_args()

columns = ["season_type", "posteam", "defteam", "pass", "rush", "epa", "qb_dropback", "sack"]
plays = scrimmage_plays(load_pbp(args.season, columns=columns))
dropbacks = plays[plays["qb_dropback"] == 1]
allowed = dropbacks.groupby("posteam")["sack"].mean().rename("allowed")
made = dropbacks.groupby("defteam")["sack"].mean().rename("made")
teams = allowed.to_frame().join(made).reset_index(names="team")
league = dropbacks["sack"].mean()
print(teams.sort_values("made", ascending=False).round(3).to_string(index=False))

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
team_scatter(ax, teams["allowed"], teams["made"], teams["team"])
mean_lines(ax, league, league)
ax.invert_xaxis()  # allowing fewer sacks is better, so put clean pockets on the right
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_xlabel("Sack rate allowed by the offense  (right is better)")
ax.set_ylabel("Sack rate by the defense  (up is better)")
corner_notes(ax, top_right="Win both lines", bottom_left="Lose both lines",
             top_left="Pass rush, no protection", bottom_right="Protection, no pass rush")
titles(ax, f"Winning the pocket, {args.season}",
       "Sacks as a share of dropbacks, regular season. Dashed lines are the league average.")
finish(fig, f"19_sack_rates_{args.season}", args.show)
