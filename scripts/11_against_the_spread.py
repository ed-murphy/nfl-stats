"""Who beats the betting line? Average margin against the spread.

The closing point spread is the market's best guess at each game's margin,
so a team's average result relative to it shows who has been better (or
worse) than expected all season. Each label carries the team's record
against the spread (wins-losses-pushes).
"""

import matplotlib.pyplot as plt
import pandas as pd

from nflstats import load_schedules, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, diverging_barh, finish, titles

args = base_parser(__doc__).parse_args()

games = regular_season(load_schedules(args.season))
games = games[games["result"].notna() & games["spread_line"].notna()]
# spread_line is the points the home team is favored by; result is home minus away score.
home_cover = games["result"] - games["spread_line"]
covers = pd.concat([
    pd.DataFrame({"team": games["home_team"], "cover": home_cover}),
    pd.DataFrame({"team": games["away_team"], "cover": -home_cover}),
])

teams = covers.groupby("team")["cover"].agg(
    margin="mean",
    wins=lambda c: (c > 0).sum(),
    losses=lambda c: (c < 0).sum(),
    pushes=lambda c: (c == 0).sum(),
).sort_values("margin", ascending=False)
print(teams.round(2).to_string())

record = teams["wins"].astype(str) + "-" + teams["losses"].astype(str)
record = record.where(teams["pushes"] == 0, record + "-" + teams["pushes"].astype(str))
margin = teams["margin"].set_axis(teams.index + "  " + record)

apply_style()
fig, ax = plt.subplots(figsize=(9, 9.5))
diverging_barh(ax, margin, fmt="{:+.1f}")
ax.set_xlabel("Average points better than the spread, per game")
titles(ax, f"Who beats the betting line? {args.season}",
       "Average margin relative to the closing spread, regular season. Labels show record against the spread.")
finish(fig, f"11_against_the_spread_{args.season}", args.show)
