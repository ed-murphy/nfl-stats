"""Snap counts by week: a plain table of who was on the field for one team.

One row per player, ordered by total snaps for the season, with the total
in its own column followed by a column for each game. Blank cells mean the
player took no snaps that week. Counts offense, defense and special-teams
snaps together unless ``--unit`` narrows it. Defaults to the Eagles.
"""

import matplotlib.pyplot as plt
import pandas as pd

from nflstats import load_snap_counts
from nflstats.cli import base_parser
from nflstats.plotting import AXIS, GRID, INK, INK_2, MUTED, apply_style, finish, titles

UNITS = {"all": ["offense", "defense", "st"], "offense": ["offense"], "defense": ["defense"], "st": ["st"]}
UNIT_NAMES = {"all": "Offense, defense and special-teams snaps", "offense": "Offense snaps",
              "defense": "Defense snaps", "st": "Special-teams snaps"}

parser = base_parser(__doc__)
parser.add_argument("--team", default="PHI", help="team abbreviation (default PHI)")
parser.add_argument("--unit", choices=UNITS, default="all", help="which snaps to count (default all)")
args = parser.parse_args()
team = args.team.upper()

snaps = load_snap_counts(args.season)
if team not in set(snaps["team"]):
    raise SystemExit(f"unknown team {team!r}; choose from: {', '.join(sorted(snaps['team'].unique()))}")
snaps = snaps[snaps["team"] == team]
snaps = snaps.assign(snaps=snaps[[f"{unit}_snaps" for unit in UNITS[args.unit]]].sum(axis=1))

# game_id is <season>_<week>_<away>_<home>.
games = snaps.drop_duplicates("week").set_index("week").sort_index()
headers = [f"Wk {week}\n{opp if game_id.endswith(team) else '@' + opp}"
           for week, opp, game_id in zip(games.index, games["opponent"], games["game_id"])]

played = snaps[snaps["snaps"] > 0]
info = played.groupby("pfr_player_id")[["player", "position"]].first()
counts = played.pivot(index="pfr_player_id", columns="week", values="snaps").reindex(columns=games.index)
info["total"] = counts.sum(axis=1)
info = info.sort_values(["total", "player"], ascending=[False, True])
counts = counts.loc[info.index]

table = counts.map(lambda value: "" if pd.isna(value) else f"{value:.0f}")
table.columns = [header.replace("\n", " ") for header in headers]
table.insert(0, "Total", info["total"].astype(int))
table.insert(0, "Pos", info["position"])
table.index = info["player"].rename(None)
print(f"{team} snap counts, {args.season} ({UNIT_NAMES[args.unit].lower()})")
print(table.to_string())

# Column positions, in the same units as one weekly column's width.
name_x, pos_x, total_x, first_week_x = 0.0, 3.5, 4.5, 5.6
week_x = [first_week_x + i for i in range(len(headers))]

apply_style()
fig, ax = plt.subplots(figsize=(4.6 + 0.62 * len(headers), 1.6 + 0.235 * len(table)))
ax.set_xlim(-0.1, week_x[-1] + 0.5)
ax.set_ylim(len(table) - 0.5, -2.4)
ax.axis("off")

for x, label, ha in [(name_x, "Player", "left"), (pos_x, "Pos", "center"), (total_x, "Total", "center"),
                     *[(x, header, "center") for x, header in zip(week_x, headers)]]:
    ax.text(x, -0.75, label, ha=ha, va="bottom", fontsize=8.5, color=INK if label == "Total" else MUTED,
            fontweight="bold" if label == "Total" else "normal", linespacing=1.3)
ax.axhline(-0.55, color=AXIS, linewidth=1)

for row, (player, cells) in enumerate(table.iterrows()):
    if row % 2:
        ax.axhspan(row - 0.5, row + 0.5, color=GRID, alpha=0.4, linewidth=0)
    ax.text(name_x, row, player, ha="left", va="center", fontsize=9, color=INK)
    ax.text(pos_x, row, cells["Pos"], ha="center", va="center", fontsize=8.5, color=MUTED)
    ax.text(total_x, row, f"{cells['Total']:,}", ha="center", va="center", fontsize=9, fontweight="bold")
    for x, value in zip(week_x, cells.iloc[2:]):
        ax.text(x, row, value, ha="center", va="center", fontsize=9, color=INK_2)

titles(ax, f"{team} snap counts by week, {args.season}",
       f"{UNIT_NAMES[args.unit]}, ordered by season total.")
suffix = "" if args.unit == "all" else f"_{args.unit}"
finish(fig, f"21_snap_counts_{team}_{args.season}{suffix}", args.show)
