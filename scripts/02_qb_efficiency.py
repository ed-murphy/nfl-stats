"""Quarterback efficiency: EPA per dropback vs completion % over expected.

EPA per dropback measures total value (including sacks and scrambles);
CPOE measures accuracy after adjusting for throw difficulty. Quarterbacks
high on both are winning with their arm rather than their scheme.
"""

import matplotlib.pyplot as plt

from nflstats import load_pbp, scrimmage_plays
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, finish, mean_lines, team_scatter, titles

parser = base_parser(__doc__)
parser.add_argument("--min-per-week", type=float, default=14, help="qualifying dropbacks per week played (default 14)")
args = parser.parse_args()

columns = ["season_type", "week", "posteam", "pass", "rush", "epa", "qb_dropback", "id", "name", "cpoe"]
plays = scrimmage_plays(load_pbp(args.season, columns=columns))
dropbacks = plays[(plays["qb_dropback"] == 1) & plays["id"].notna()]

qbs = dropbacks.groupby("id").agg(
    name=("name", "last"),
    team=("posteam", "last"),
    dropbacks=("epa", "size"),
    epa=("epa", "mean"),
    cpoe=("cpoe", "mean"),
)
minimum = args.min_per_week * plays["week"].max()
qbs = qbs[qbs["dropbacks"] >= minimum]

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
team_scatter(ax, qbs["cpoe"], qbs["epa"], qbs["team"], labels=qbs["name"], size=qbs["dropbacks"] / 4)
mean_lines(ax, qbs["cpoe"].mean(), qbs["epa"].mean())
ax.set_xlabel("Completion % over expected")
ax.set_ylabel("EPA per dropback")
titles(ax, f"Quarterback efficiency, {args.season}",
       f"Regular season, minimum {minimum:.0f} dropbacks. Dot size is dropback volume; dashed lines are group averages.")
finish(fig, f"02_qb_efficiency_{args.season}", args.show)
