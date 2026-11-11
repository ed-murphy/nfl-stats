"""Team tiers: offensive vs defensive EPA per play.

Expected points added (EPA) per play is the best single-number summary of
how good a unit is. Plotting offense against defense sorts the league into
contenders (top right) and rebuilders (bottom left).
"""

import matplotlib.pyplot as plt

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, corner_notes, finish, mean_lines, team_scatter, titles

args = base_parser(__doc__).parse_args()

plays = scrimmage_plays(load_pbp(args.season, columns=["season_type", "posteam", "defteam", "pass", "rush", "epa"]))
offense = plays.groupby("posteam")["epa"].mean().rename("off_epa")
defense = plays.groupby("defteam")["epa"].mean().rename("def_epa")
teams = offense.to_frame().join(defense).reset_index(names="team")

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
team_scatter(ax, teams["off_epa"], teams["def_epa"], teams["team"])
mean_lines(ax, teams["off_epa"].mean(), teams["def_epa"].mean())
ax.invert_yaxis()  # allowing fewer points is better, so put good defenses on top
ax.set_xlabel("Offense EPA per play  (right is better)")
ax.set_ylabel("Defense EPA per play allowed  (up is better)")
corner_notes(ax, top_right="Good offense, good defense", bottom_left="Bad offense, bad defense",
             top_left="Defense carries", bottom_right="Offense carries")
titles(ax, f"NFL team tiers, {args.season}", "Expected points added per play, regular season. Dashed lines are league averages.")
finish(fig, f"01_team_tiers_{args.season}", args.show)
