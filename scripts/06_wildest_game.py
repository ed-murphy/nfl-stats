"""The wildest game of the season, as a win-probability chart.

Ranks every game by total win-probability movement (the sum of every swing,
play to play) and charts the top one. Pass --game-id to chart a specific
game instead, e.g. --game-id 2025_01_DAL_PHI.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp
from nflstats.cli import base_parser
from nflstats.plotting import AXIS, INK_2, SERIES, apply_style, finish, titles

parser = base_parser(__doc__)
parser.add_argument("--game-id", help="nflverse game id (default: the season's wildest game)")
args = parser.parse_args()

columns = ["game_id", "week", "home_team", "away_team", "qtr", "quarter_seconds_remaining",
           "game_seconds_remaining", "home_wp", "total_home_score", "total_away_score"]
pbp = load_pbp(args.season, columns=columns).dropna(subset=["home_wp"])

if args.game_id:
    game_id = args.game_id
else:
    movement = pbp.groupby("game_id")["home_wp"].agg(lambda wp: wp.diff().abs().sum())
    game_id = movement.idxmax()
    print("most win-probability movement:")
    print(movement.nlargest(5).round(2).to_string())

game = pbp[pbp["game_id"] == game_id].copy()
if game.empty:
    raise SystemExit(f"no plays found for game {game_id} in {args.season}")

# Minutes elapsed; overtime continues past 60.
overtime = game["qtr"] > 4
ot_length = game.loc[overtime, "quarter_seconds_remaining"].max() if overtime.any() else 0
game["minute"] = (3600 - game["game_seconds_remaining"]) / 60
game.loc[overtime, "minute"] = 60 + (ot_length - game.loc[overtime, "quarter_seconds_remaining"]) / 60

home, away, week = game["home_team"].iloc[0], game["away_team"].iloc[0], game["week"].iloc[0]
home_score, away_score = int(game["total_home_score"].max()), int(game["total_away_score"].max())

apply_style()
fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(game["minute"], game["home_wp"], color=SERIES[0])
ax.axhline(0.5, color=AXIS, linewidth=1)
end = game["minute"].max()
quarters = [15, 30, 45] + ([60] if overtime.any() else [])
for minute in quarters:
    ax.axvline(minute, color=AXIS, linewidth=1, linestyle=(0, (4, 3)))
ticks = [7.5, 22.5, 37.5, 52.5] + ([(60 + end) / 2] if overtime.any() else [])
ax.set_xticks(ticks, ["Q1", "Q2", "Q3", "Q4", "OT"][: len(ticks)])
ax.set_xlim(0, max(end, 60) * 1.005)
ax.set_ylim(0, 1.01)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.grid(axis="x", visible=False)
ax.set_ylabel(f"{home} win probability")
ax.text(0.008, 0.97, f"{home} winning", transform=ax.transAxes, va="top", fontsize=9.5, color=INK_2)
ax.text(0.008, 0.03, f"{away} winning", transform=ax.transAxes, va="bottom", fontsize=9.5, color=INK_2)
titles(ax, f"{away} {away_score}, {home} {home_score}",
       f"{args.season} week {week}, {away} at {home}. Home-team win probability after every play.")
finish(fig, f"06_wildest_game_{game_id}", args.show)
