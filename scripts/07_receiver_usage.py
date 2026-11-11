"""Receiver usage: target share vs air-yards share.

Target share says how often a receiver is thrown to; air-yards share says
how much of the team's downfield passing runs through them. Players above
the diagonal are deep threats, players below it are underneath volume
targets.
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

from nflstats import load_pbp, regular_season
from nflstats.cli import base_parser
from nflstats.plotting import AXIS, apply_style, corner_notes, finish, team_scatter, titles

parser = base_parser(__doc__)
parser.add_argument("--top", type=int, default=36, help="number of receivers to show, by targets (default 36)")
args = parser.parse_args()

columns = ["season_type", "posteam", "play_type", "receiver_player_id", "receiver_player_name", "air_yards"]
pbp = regular_season(load_pbp(args.season, columns=columns))
targets = pbp[(pbp["play_type"] == "pass") & pbp["receiver_player_id"].notna() & pbp["air_yards"].notna()]

players = targets.groupby(["receiver_player_id", "posteam"]).agg(
    name=("receiver_player_name", "last"),
    targets=("air_yards", "size"),
    air_yards=("air_yards", "sum"),
).reset_index()
team = targets.groupby("posteam")["air_yards"].agg(team_targets="size", team_air_yards="sum")
players = players.join(team, on="posteam")
players["target_share"] = players["targets"] / players["team_targets"]
players["air_share"] = players["air_yards"] / players["team_air_yards"]
top = players.nlargest(args.top, "targets")

apply_style()
fig, ax = plt.subplots(figsize=(10, 8))
low = min(top["target_share"].min(), top["air_share"].min()) - 0.02
high = max(top["target_share"].max(), top["air_share"].max()) + 0.03
ax.plot([low, high], [low, high], color=AXIS, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
team_scatter(ax, top["target_share"], top["air_share"], top["posteam"], labels=top["name"])
ax.set_xlim(low, high)
ax.set_ylim(low, high)
ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_xlabel("Share of team targets")
ax.set_ylabel("Share of team air yards")
corner_notes(ax, top_left="Deep threats", bottom_right="Underneath volume")
titles(ax, f"Who owns their team's passing game? {args.season}",
       f"Top {args.top} players by targets, regular season. Shares are within each player's own team.")
finish(fig, f"07_receiver_usage_{args.season}", args.show)
