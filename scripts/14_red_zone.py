"""Red zone: who gets there, and who finishes?

Red-zone trips per game (drives that reach the opponent's 20) against the
share of those trips that end in a touchdown. Getting there reflects the
whole offense; finishing is a smaller sample that swings more from year to
year, so teams far above or below the pack on the vertical axis tend to
drift back.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import apply_style, corner_notes, finish, mean_lines, team_scatter, titles

args = base_parser(__doc__).parse_args()

columns = ["season_type", "game_id", "posteam", "down", "yardline_100", "fixed_drive", "fixed_drive_result"]
pbp = regular_season(load_pbp(args.season, columns=columns))
games = pbp.dropna(subset=["posteam"]).groupby("posteam")["game_id"].nunique().rename("games")
inside = pbp[pbp["down"].notna() & (pbp["yardline_100"] <= 20)]
trips = inside.groupby(["posteam", "game_id", "fixed_drive"])["fixed_drive_result"].first().reset_index()
trips["td"] = trips["fixed_drive_result"] == "Touchdown"

teams = trips.groupby("posteam").agg(trips=("td", "size"), tds=("td", "sum")).join(games)
teams["trips_per_game"] = teams["trips"] / teams["games"]
teams["td_rate"] = teams["tds"] / teams["trips"]
teams = teams.reset_index(names="team")
print(teams.sort_values("td_rate", ascending=False).round(3).to_string(index=False))

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
team_scatter(ax, teams["trips_per_game"], teams["td_rate"], teams["team"])
mean_lines(ax, teams["trips_per_game"].mean(), teams["tds"].sum() / teams["trips"].sum())
ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_xlabel("Red-zone trips per game  (right is better)")
ax.set_ylabel("Touchdown rate per trip  (up is better)")
corner_notes(ax, top_right="Get there and finish", bottom_left="Rarely there, settle for three",
             top_left="Rare but lethal", bottom_right="Stall at the doorstep")
titles(ax, f"Red zone: who gets there, and who finishes? {args.season}",
       "Drives reaching the opponent's 20 and the share ending in a touchdown, regular season. "
       "Dashed lines are league averages.")
finish(fig, f"14_red_zone_{args.season}", args.show)
