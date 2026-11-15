"""How quarterbacks get their yards: throw depth vs yards after the catch.

Average depth of target (air yards per attempt) against yards after the
catch per completion. Passers at the bottom right push the ball downfield
themselves; those at the top left throw short and let receivers and scheme
do the work.
"""

import matplotlib.pyplot as plt

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, corner_notes, finish, mean_lines, team_scatter, titles

parser = base_parser(__doc__)
parser.add_argument("--min-per-week", type=float, default=12, help="qualifying attempts per week played (default 12)")
args = parser.parse_args()

columns = ["season_type", "week", "posteam", "passer_player_id", "passer_player_name", "air_yards",
           "complete_pass", "yards_after_catch"]
pbp = regular_season(load_pbp(args.season, columns=columns))
throws = pbp[pbp["passer_player_id"].notna() & pbp["air_yards"].notna()]

qbs = throws.groupby("passer_player_id").agg(
    name=("passer_player_name", "last"),
    team=("posteam", "last"),
    attempts=("air_yards", "size"),
    adot=("air_yards", "mean"),
    yac=("yards_after_catch", "mean"),  # only recorded on completions
)
minimum = args.min_per_week * pbp["week"].max()
qbs = qbs[qbs["attempts"] >= minimum]
print(qbs.sort_values("adot", ascending=False).round(2).to_string(index=False))

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
team_scatter(ax, qbs["adot"], qbs["yac"], qbs["team"], labels=qbs["name"], size=qbs["attempts"] / 3)
mean_lines(ax, qbs["adot"].mean(), qbs["yac"].mean())
ax.margins(0.09)  # keep outlier labels clear of the corner notes
ax.set_xlabel("Average depth of target (air yards per attempt)")
ax.set_ylabel("Yards after catch per completion")
corner_notes(ax, top_right="Deep throws and run-after-catch", bottom_left="Short throws, little after the catch",
             top_left="Short throws, receivers do the rest", bottom_right="Yards come through the air")
titles(ax, f"How quarterbacks get their yards, {args.season}",
       f"Regular season, minimum {minimum:.0f} attempts. Dot size is attempt volume; dashed lines are group averages.")
finish(fig, f"18_qb_depth_and_yac_{args.season}", args.show)
