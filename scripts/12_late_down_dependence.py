"""Which offenses are living on third down?

Early-down (1st and 2nd) efficiency is stable from week to week; third- and
fourth-down efficiency is much noisier. An offense that is ordinary on
early downs but keeps converting late downs is a candidate to cool off,
and one that is good early but failing late is likely better than its
results.
"""

import matplotlib.pyplot as plt

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, corner_notes, finish, mean_lines, team_scatter, titles

args = base_parser(__doc__).parse_args()

plays = scrimmage_plays(load_pbp(args.season, columns=["season_type", "posteam", "down", "pass", "rush", "epa"]))
plays = plays[plays["down"].notna()]
early = plays[plays["down"] <= 2].groupby("posteam")["epa"].mean().rename("early")
late = plays[plays["down"] >= 3].groupby("posteam")["epa"].mean().rename("late")
teams = early.to_frame().join(late).reset_index(names="team")
teams["gap"] = teams["late"] - teams["early"]
print(teams.sort_values("gap", ascending=False).round(3).to_string(index=False))

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
team_scatter(ax, teams["early"], teams["late"], teams["team"])
mean_lines(ax, teams["early"].mean(), teams["late"].mean())
ax.set_xlabel("EPA per play on 1st and 2nd down  (right is better)")
ax.set_ylabel("EPA per play on 3rd and 4th down  (up is better)")
corner_notes(ax, top_right="Good on every down", bottom_left="Bad on every down",
             top_left="Bailed out by late downs", bottom_right="Let down by late downs")
titles(ax, f"Which offenses are living on third down? {args.season}",
       "Offensive EPA per play by down, regular season. Dashed lines are league averages.")
finish(fig, f"12_late_down_dependence_{args.season}", args.show)
