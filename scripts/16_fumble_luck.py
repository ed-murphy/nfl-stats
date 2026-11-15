"""Fumble luck: who is getting the bounces?

Forcing fumbles is a skill, but who falls on a loose ball is close to
random. This counts every fumble in a team's games and compares the number
the team recovered with what league-average recovery rates would give
(the fumbling side keeps roughly half). Big positive or negative
numbers are turnover margin that is unlikely to last. Fumbles out of
bounds are ignored.
"""

import matplotlib.pyplot as plt
import numpy as np

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, diverging_barh, finish, titles

args = base_parser(__doc__).parse_args()

columns = ["season_type", "posteam", "defteam", "fumble", "fumble_out_of_bounds", "fumbled_1_team",
           "fumble_recovery_1_team"]
pbp = regular_season(load_pbp(args.season, columns=columns))
fumbles = pbp[(pbp["fumble"] == 1) & (pbp["fumble_out_of_bounds"] != 1)
              & pbp["fumbled_1_team"].notna() & pbp["fumble_recovery_1_team"].notna()].copy()
fumbles["opponent"] = np.where(fumbles["fumbled_1_team"] == fumbles["posteam"], fumbles["defteam"], fumbles["posteam"])
fumbles["kept"] = fumbles["fumble_recovery_1_team"] == fumbles["fumbled_1_team"]
keep_rate = fumbles["kept"].mean()

own = fumbles.groupby("fumbled_1_team")["kept"].agg(own_fumbles="size", own_recovered="sum")
opp = fumbles.groupby("opponent")["kept"].agg(opp_fumbles="size", opp_kept="sum")
teams = own.join(opp, how="outer").fillna(0)
teams["recovered"] = teams["own_recovered"] + teams["opp_fumbles"] - teams["opp_kept"]
teams["expected"] = teams["own_fumbles"] * keep_rate + teams["opp_fumbles"] * (1 - keep_rate)
teams["luck"] = teams["recovered"] - teams["expected"]
teams = teams.sort_values("luck", ascending=False)
print(f"fumbling team keeps the ball {keep_rate:.1%} of the time")
print(teams.round(2).to_string())

total = (teams["own_fumbles"] + teams["opp_fumbles"]).astype(int).astype(str)
luck = teams["luck"].set_axis(teams.index + "  " + teams["recovered"].astype(int).astype(str) + " of " + total)

apply_style()
fig, ax = plt.subplots(figsize=(9, 9.5))
diverging_barh(ax, luck, fmt="{:+.1f}")
ax.set_xlabel("Fumbles recovered above expectation")
titles(ax, f"Who is getting the bounces? {args.season}",
       "Fumbles recovered minus expected, regular season. Labels: recovered of all fumbles in the team's games.")
finish(fig, f"16_fumble_luck_{args.season}", args.show)
