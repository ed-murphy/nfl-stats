"""Play-calling identity: pass rate over expected (PROE) by team.

nflverse models how likely a pass is on every play given down, distance,
score and clock. A team's average gap between what it called and what was
expected shows whether the coaching staff leans pass or run, independent of
game script.
"""

import matplotlib.pyplot as plt

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, diverging_barh, finish, titles

args = base_parser(__doc__).parse_args()

plays = scrimmage_plays(load_pbp(args.season, columns=["season_type", "posteam", "pass", "rush", "epa", "pass_oe"]))
proe = plays.groupby("posteam")["pass_oe"].mean().sort_values(ascending=False)

apply_style()
fig, ax = plt.subplots(figsize=(9, 9.5))
diverging_barh(ax, proe)
ax.set_xlabel("Pass rate over expected (percentage points)")
titles(ax, f"Who throws more than the situation calls for? {args.season}",
       "Pass rate over expected, regular season. Blue teams lean pass, red teams lean run.")
finish(fig, f"05_pass_rate_over_expected_{args.season}", args.show)
