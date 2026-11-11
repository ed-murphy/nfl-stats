"""Shared matplotlib style and helpers so every plot looks like part of one set."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from nflstats.data import ROOT, load_teams

PLOTS_DIR = ROOT / "plots"

# Ink and chrome
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Categorical series, used in this order (don't cycle past the end).
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
# Ordered categories (e.g. eras), light to dark in one hue.
ORDINAL = ["#86b6ef", "#2a78d6", "#104281"]
# Opposite directions around zero.
POSITIVE = "#2a78d6"
NEGATIVE = "#e34948"


def _first_installed(fonts: list[str]) -> str:
    installed = {font.name for font in font_manager.fontManager.ttflist}
    return next((font for font in fonts if font in installed), "sans-serif")


def apply_style() -> None:
    """Set the house matplotlib style. Call once at the top of a script."""
    plt.rcParams.update(
        {
            "figure.figsize": (10, 6.5),
            "figure.dpi": 100,
            "savefig.dpi": 160,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "font.family": _first_installed(["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"]),
            "font.size": 10,
            "text.color": INK,
            "axes.edgecolor": AXIS,
            "axes.labelcolor": INK_2,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": MUTED,
            "ytick.labelcolor": MUTED,
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "lines.linewidth": 2,
            "lines.markersize": 6,
            "legend.frameon": False,
            "legend.labelcolor": INK_2,
        }
    )


def titles(ax: Axes, title: str, subtitle: str = "") -> None:
    """Left-aligned bold title with a one-line subtitle under it."""
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", pad=30 if subtitle else 12)
    if subtitle:
        ax.text(0, 1.0, subtitle, transform=ax.transAxes, va="bottom", fontsize=10.5, color=INK_2,
                linespacing=1.9)


def finish(fig: Figure, name: str, show: bool = False) -> Path:
    """Add the data credit, save to ``plots/<name>.png`` and optionally open a window."""
    fig.tight_layout()
    _place_labels(fig)
    fig.text(0.995, 0.008, "Data: nflverse", ha="right", va="bottom", fontsize=8, color=MUTED)
    PLOTS_DIR.mkdir(exist_ok=True)
    path = PLOTS_DIR / f"{name}.png"
    fig.savefig(path)
    print(f"saved {path.relative_to(ROOT)}")
    if show:
        plt.show()
    plt.close(fig)
    return path


def team_colors() -> dict[str, str]:
    """Primary color for each team abbreviation."""
    teams = load_teams()
    return dict(zip(teams["team_abbr"], teams["team_color"]))


# Scatter labels wait here until finish(), when axis limits and layout are final.
_pending_labels: list[tuple[Axes, np.ndarray, np.ndarray, list[str], np.ndarray]] = []


def team_scatter(ax: Axes, x: pd.Series, y: pd.Series, teams: pd.Series, labels: pd.Series | None = None,
                 size: float | pd.Series = 90) -> None:
    """Scatter of dots in team colors, each with a text label (team abbreviation by default).

    Labels are positioned by ``finish()`` so that they avoid each other and the dots.
    """
    colors = team_colors()
    ax.scatter(x, y, s=size, c=[colors.get(t, MUTED) for t in teams], edgecolors=SURFACE,
               linewidths=1.5, zorder=3)
    sizes = np.broadcast_to(np.asarray(size, dtype=float), (len(x),))
    names = [str(label) for label in (teams if labels is None else labels)]
    _pending_labels.append((ax, np.asarray(x, dtype=float), np.asarray(y, dtype=float), names, sizes))


def _overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    width = min(a[2], b[2]) - max(a[0], b[0])
    height = min(a[3], b[3]) - max(a[1], b[1])
    return width * height if width > 0 and height > 0 else 0.0


def _place_labels(fig: Figure, fontsize: float = 8.5) -> None:
    """Put each pending scatter label on the side of its dot with the least overlap."""
    mine = [entry for entry in _pending_labels if entry[0].figure is fig]
    if not mine:
        return
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    to_points = 72 / fig.dpi
    for entry in mine:
        _pending_labels.remove(entry)
        ax, xs, ys, names, sizes = entry
        centers = ax.transData.transform(np.column_stack([xs, ys]))
        radii = np.sqrt(sizes) / 2 / to_points + 1  # scatter sizes are areas in points^2
        taken = [(cx - r, cy - r, cx + r, cy + r) for (cx, cy), r in zip(centers, radii)]
        frame = ax.bbox.extents
        for (cx, cy), radius, name in zip(centers, radii, names):
            probe = ax.text(0, 0, name, fontsize=fontsize)
            extent = probe.get_window_extent(renderer)
            probe.remove()
            w, h = extent.width, extent.height
            near, diag = radius + 3, radius * 0.7 + 2
            offsets = [(0, near + h / 2), (0, -near - h / 2), (near + w / 2, 0), (-near - w / 2, 0),
                       (diag + w / 2, diag + h / 2), (-diag - w / 2, diag + h / 2),
                       (diag + w / 2, -diag - h / 2), (-diag - w / 2, -diag - h / 2)]

            def cost(offset: tuple[float, float]) -> float:
                bx, by = cx + offset[0], cy + offset[1]
                box = (bx - w / 2, by - h / 2, bx + w / 2, by + h / 2)
                outside = w * h - _overlap(box, tuple(frame))
                return sum(_overlap(box, other) for other in taken) + 5 * outside

            dx, dy = min(offsets, key=cost)  # ties keep the earliest option: above the dot
            taken.append((cx + dx - w / 2, cy + dy - h / 2, cx + dx + w / 2, cy + dy + h / 2))
            ax.annotate(name, ax.transData.inverted().transform((cx, cy)), xytext=(dx * to_points, dy * to_points),
                        textcoords="offset points", ha="center", va="center", fontsize=fontsize,
                        color=INK_2, zorder=4)


def mean_lines(ax: Axes, x: float, y: float) -> None:
    """Dashed crosshair marking the league average on a scatter."""
    ax.axvline(x, color=AXIS, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    ax.axhline(y, color=AXIS, linewidth=1, linestyle=(0, (4, 3)), zorder=1)


def corner_notes(ax: Axes, top_right: str = "", bottom_left: str = "", top_left: str = "",
                 bottom_right: str = "") -> None:
    """Small muted captions naming what each quadrant of a scatter means."""
    spots = {
        (0.99, 0.98, "right", "top"): top_right,
        (0.01, 0.02, "left", "bottom"): bottom_left,
        (0.01, 0.98, "left", "top"): top_left,
        (0.99, 0.02, "right", "bottom"): bottom_right,
    }
    for (px, py, ha, va), text in spots.items():
        if text:
            ax.text(px, py, text, transform=ax.transAxes, ha=ha, va=va, fontsize=9, color=MUTED,
                    style="italic")


def diverging_barh(ax: Axes, values: pd.Series, fmt: str = "{:+.1f}") -> None:
    """Horizontal bars around zero, sorted as given, with the value written at each bar end.

    ``values`` is indexed by label; the first row is drawn at the top.
    """
    values = values.iloc[::-1]
    colors = [POSITIVE if v >= 0 else NEGATIVE for v in values]
    ax.barh(values.index, values, color=colors, height=0.72)
    ax.axvline(0, color=AXIS, linewidth=1)
    pad = values.abs().max() * 0.015
    for label, v in values.items():
        ax.text(v + (pad if v >= 0 else -pad), label, fmt.format(v), va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=INK_2)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.margins(x=0.08, y=0.01)
