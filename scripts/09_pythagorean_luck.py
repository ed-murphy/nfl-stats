"""Lucky and unlucky teams: actual wins vs Pythagorean expectation.

Points scored and allowed predict future record better than record itself.
Expected win % = PF^2.37 / (PF^2.37 + PA^2.37). Teams well above their
expectation have been winning close games and tend to regress; teams well
below it are better than their record.
"""

import matplotlib.pyplot as plt
import pandas as pd

from nflstats import load_schedules, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, diverging_barh, finish, titles

EXPONENT = 2.37

args = base_parser(__doc__).parse_args()

games = regular_season(load_schedules(args.season))
games = games[games["result"].notna()]
home = pd.DataFrame({"team": games["home_team"], "pf": games["home_score"], "pa": games["away_score"]})
away = pd.DataFrame({"team": games["away_team"], "pf": games["away_score"], "pa": games["home_score"]})
results = pd.concat([home, away])
results["win"] = (results["pf"] > results["pa"]) + 0.5 * (results["pf"] == results["pa"])

teams = results.groupby("team").agg(games=("win", "size"), wins=("win", "sum"), pf=("pf", "sum"), pa=("pa", "sum"))
expected_pct = teams["pf"] ** EXPONENT / (teams["pf"] ** EXPONENT + teams["pa"] ** EXPONENT)
teams["expected_wins"] = expected_pct * teams["games"]
teams["luck"] = teams["wins"] - teams["expected_wins"]
teams = teams.sort_values("luck", ascending=False)
print(teams.round(2).to_string())

apply_style()
fig, ax = plt.subplots(figsize=(9, 9.5))
diverging_barh(ax, teams["luck"], fmt="{:+.1f}")
ax.set_xlabel("Wins above Pythagorean expectation")
titles(ax, f"Who is winning more than their points say? {args.season}",
       "Actual wins minus wins expected from points scored and allowed, regular season.")
finish(fig, f"09_pythagorean_luck_{args.season}", args.show)
