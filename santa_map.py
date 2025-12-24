"""
Holiday Santa Traditions Map (Cartopy + extra Christmas spirit)
"""

from __future__ import annotations

import os
import random
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.geodesic import Geodesic

from shapely.geometry import Point
from shapely.ops import unary_union


# ----------------------------
# Config
# ----------------------------
OUT_PNG = "santa_traditions_map_christmas.png"
OUT_GIF = "santa_traditions_map_snowfall.gif"

# “influence” radius in km (geodesic circles)
BUFFER_KM = 350

# Land snowflakes
LAND_SNOWFLAKES = 1400
LAND_SNOWFLAKE_ALPHA = 0.12

# Animated snowfall
SNOW_PARTICLES = 450
SNOW_FRAMES = 120
SNOW_INTERVAL_MS = 55
SNOWFALL_ALPHA = 0.45


# ----------------------------
# Helpers
# ----------------------------
def _geodesic_circle(lon: float, lat: float, radius_km: float, n_samples: int = 120):
    """Return Nx2 lon/lat circle polygon points around (lon,lat) with geodesic radius."""
    g = Geodesic()
    coords = g.circle(lon=lon, lat=lat, radius=radius_km * 1000.0, n_samples=n_samples)
    return coords  # Nx2 lon/lat


def _legend_handles(color_map: dict[str, tuple[float, float, float, float]]):
    handles = []
    for k, c in color_map.items():
        h = mlines.Line2D(
            [], [],
            color=c,
            marker="o",
            linestyle="None",
            markersize=10,
            markeredgecolor="white",
            markeredgewidth=1.2,
            label=k,
        )
        handles.append(h)
    return handles


def _make_festive_color_map(traditions: list[str]):
    """
    Christmas-y-ish palette: reds, greens, golds, icy blues, purples, plus a 'summer' color.
    """
    palette = [
        (0.80, 0.15, 0.20, 1.0),  # cranberry
        (0.10, 0.50, 0.28, 1.0),  # pine
        (0.96, 0.74, 0.20, 1.0),  # gold
        (0.35, 0.70, 0.86, 1.0),  # icy blue
        (0.55, 0.35, 0.78, 1.0),  # winter purple
        (0.95, 0.48, 0.18, 1.0),  # warm orange
        (0.20, 0.20, 0.25, 1.0),  # charcoal
        (0.90, 0.30, 0.55, 1.0),  # berry pink
    ]
    cmap = {t: palette[i % len(palette)] for i, t in enumerate(traditions)}

    # Force a distinct "summer" color if present
    if "Southern Hemisphere" in cmap:
        cmap["Southern Hemisphere"] = (0.05, 0.75, 0.65, 1.0)  # bright teal/aqua


    return cmap


def _build_land_union():
    """Union of Natural Earth land polygons (coarse = fast)."""
    land = cfeature.NaturalEarthFeature("physical", "land", "110m")
    geoms = list(land.geometries())
    return unary_union(geoms)


def _sample_points_in_land(land_union, n: int, seed: int = 7):
    """Rejection sample lon/lat points that fall on land (decorative)."""
    rng = random.Random(seed)
    pts = []
    minx, miny, maxx, maxy = -180, -60, 180, 85
    tries = 0
    max_tries = n * 60

    while len(pts) < n and tries < max_tries:
        tries += 1
        lon = rng.uniform(minx, maxx)
        lat = rng.uniform(miny, maxy)
        if land_union.contains(Point(lon, lat)):
            pts.append((lon, lat))

    if len(pts) < n:
        warnings.warn(f"Only sampled {len(pts)}/{n} land snowflakes (increase max_tries if needed).")
    return np.array(pts)


def _draw_santa_hat(ax, lon: float, lat: float, transform, scale_deg: float = 1.6, zorder: int = 60):
    """
    Draw a simple Santa hat near a point using patches (no emoji fonts needed).
    scale_deg roughly controls hat size in degrees (visual only).
    """
    # Hat position slightly above the point
    x0 = lon
    y0 = lat + 0.9

    # Red triangle (hat)
    tri = mpatches.Polygon(
        [(x0 - 0.55 * scale_deg, y0 - 0.10 * scale_deg),
         (x0 + 0.55 * scale_deg, y0 - 0.10 * scale_deg),
         (x0 + 0.10 * scale_deg, y0 + 0.95 * scale_deg)],
        closed=True,
        facecolor=(0.86, 0.12, 0.16, 1.0),
        edgecolor="white",
        linewidth=0.9,
        transform=transform,
        zorder=zorder,
    )
    ax.add_patch(tri)

    # White brim
    brim = mpatches.FancyBboxPatch(
        (x0 - 0.62 * scale_deg, y0 - 0.30 * scale_deg),
        1.24 * scale_deg,
        0.22 * scale_deg,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        facecolor="white",
        edgecolor="white",
        linewidth=0.6,
        transform=transform,
        zorder=zorder + 1,
    )
    ax.add_patch(brim)

    # Pom-pom
    pom = mpatches.Circle(
        (x0 + 0.15 * scale_deg, y0 + 0.93 * scale_deg),
        0.16 * scale_deg,
        facecolor="white",
        edgecolor="white",
        linewidth=0.6,
        transform=transform,
        zorder=zorder + 2,
    )
    ax.add_patch(pom)


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    # Dataset
    # Columns: name, tradition, place, lat, lon, note, official_hat(bool)
    rows = [
        # Official / famous Santa locations (hat icon)
        ("Santa Claus (Rovaniemi)", "Official Santa", "Rovaniemi, Finland", 66.5039, 25.7294, "Santa Claus Village vibes", True),
        ("Santa Claus (North Pole)", "Official Santa", "North Pole, Alaska, USA", 64.7511, -147.3494, "Santa Claus House", True),


        # Other traditions
        ("Père Noël", "Western Europe", "Strasbourg, France", 48.5734, 7.7521, "Markets + magic", False),
        ("Ded Moroz (Father Frost)", "Slavic", "Veliky Ustyug, Russia", 60.7619, 46.3056, "Father Frost", False),
        ("Papai Noel", "Americas", "Rio de Janeiro, Brazil", -22.9068, -43.1729, "Tropical Santa = short sleeves", False),
        ("Hoteiosho", "East Asia", "Tokyo, Japan", 35.6762, 139.6503, "One eye open until you're good", False),

        # Southern Hemisphere Santa (distinct summer color)
        ("Surfing Santa", "Southern Hemisphere (Summer)", "Sydney, Australia", -33.8688, 151.2093, "Beach mode Santa", True),
    ]

    df = pd.DataFrame(rows, columns=["name", "tradition", "place", "lat", "lon", "note", "official_hat"])

    traditions = sorted(df["tradition"].unique().tolist())
    color_map = _make_festive_color_map(traditions)

    # Land union for ornaments
    land_union = _build_land_union()
    land_snow_pts = _sample_points_in_land(land_union, LAND_SNOWFLAKES, seed=11)

    # Figure / projection
    proj = ccrs.Robinson()
    data_crs = ccrs.PlateCarree()

    fig = plt.figure(figsize=(15.5, 9.5), dpi=140)
    ax = plt.axes(projection=proj)
    ax.set_global()

    # Background
    ax.set_facecolor((0.06, 0.08, 0.14))  # deep winter night

    ocean_color = (0.14, 0.34, 0.48)
    land_color = (0.98, 0.98, 0.97)
    coast_color = (0.60, 0.68, 0.72)

    ax.add_feature(cfeature.OCEAN.with_scale("110m"), facecolor=ocean_color, alpha=0.95, zorder=0)
    ax.add_feature(cfeature.LAND.with_scale("110m"), facecolor=land_color, edgecolor="none", alpha=0.98, zorder=1)
    ax.add_feature(cfeature.COASTLINE.with_scale("110m"), edgecolor=coast_color, linewidth=0.8, zorder=2)
    ax.add_feature(cfeature.BORDERS.with_scale("110m"), edgecolor=(0.72, 0.74, 0.76), linewidth=0.6, alpha=0.8, zorder=2)

    # Snowflake ornaments across land (marker text can depend on fonts; if you see glyph warnings, switch marker to "*")
    ax.scatter(
        land_snow_pts[:, 0],
        land_snow_pts[:, 1],
        transform=data_crs,
        s=18,
        marker="$❄$",
        linewidths=0,
        alpha=LAND_SNOWFLAKE_ALPHA,
        zorder=3,
        color=(0.80, 0.92, 1.0),
    )
    ax.scatter(
        land_snow_pts[::2, 0],
        land_snow_pts[::2, 1],
        transform=data_crs,
        s=6,
        marker="o",
        linewidths=0,
        alpha=0.08,
        zorder=3,
        color="white",
    )

    # Buffers (geodesic circles)
    for _, r in df.iterrows():
        circle = _geodesic_circle(r["lon"], r["lat"], BUFFER_KM, n_samples=120)
        ax.fill(
            circle[:, 0],
            circle[:, 1],
            transform=data_crs,
            color=color_map[r["tradition"]],
            alpha=0.12,
            linewidth=0,
            zorder=4,
        )

    # Ornament markers by tradition
    for t in traditions:
        sub = df[df["tradition"] == t]

        # Outer glow
        ax.scatter(
            sub["lon"], sub["lat"],
            transform=data_crs,
            s=260,
            marker="o",
            color=color_map[t],
            alpha=0.20,
            linewidths=0,
            zorder=6,
        )
        # Bauble body
        ax.scatter(
            sub["lon"], sub["lat"],
            transform=data_crs,
            s=95,
            marker="o",
            color=color_map[t],
            edgecolor="white",
            linewidths=1.4,
            alpha=0.98,
            zorder=7,
        )
        # Shine highlight
        ax.scatter(
            sub["lon"] - 1.0, sub["lat"] + 0.6,
            transform=data_crs,
            s=18,
            marker="o",
            color="white",
            alpha=0.65,
            linewidths=0,
            zorder=8,
        )

    # Labels: fixed offsets only (NO movement / NO collision solving)
    base_offsets = [
        (10, 10), (10, -12), (-12, 10), (-12, -12),
        (18, 0), (-18, 0), (0, 18), (0, -18),
    ]
    arrowprops = dict(arrowstyle="-", color=(1, 1, 1, 0.35), lw=0.7, shrinkA=6, shrinkB=6)

    # 1 cm in points for Matplotlib "offset points"
    CM_TO_POINTS = 72.0 / 2.54  # 28.3464566929...

    # Per-label nudges requested
    label_nudge_points = {
        "Hoteiosho": (0.0, -CM_TO_POINTS),            # down 1 cm
        "Père Noël": (0.0, -CM_TO_POINTS),                  # down 1 cm
        "Surfing Santa": (0.0, -CM_TO_POINTS),        # down 1 cm
        "Papai Noel": (0.0, -CM_TO_POINTS),          # down 1 cm
        "Ded Moroz (Father Frost)": (CM_TO_POINTS, 0.0),  # right 1 cm
    }

    for idx, r in enumerate(df.itertuples(index=False)):
        label = f"{r.name}\n{r.place}"
        ox, oy = base_offsets[idx % len(base_offsets)]
        dx, dy = label_nudge_points.get(r.name, (0.0, 0.0))
        ox = ox + dx
        oy = oy + dy

        ax.annotate(
            label,
            (r.lon, r.lat),
            transform=data_crs,
            xytext=(ox, oy),
            textcoords="offset points",
            fontsize=9.2,
            color=(0.05, 0.08, 0.12),
            bbox=dict(boxstyle="round,pad=0.28", fc=(1, 1, 1, 0.86), ec=(1, 1, 1, 0.0)),
            arrowprops=arrowprops,
            zorder=20,
        )

    # Title + legend + footer (no emoji to avoid font warnings)
    ax.set_title("Holiday Santa Traditions Map (Fairy-tale edition)", fontsize=20, pad=18, color="white")

    handles = _legend_handles(color_map)
    handles = handles

    leg = ax.legend(
        handles=handles,
        loc="upper left",
        frameon=True,
        framealpha=0.15,
        facecolor=(0.10, 0.12, 0.18, 0.65),
        edgecolor=(1, 1, 1, 0.12),
        title="Legend",
        fontsize=10.5,
        title_fontsize=11.5,
    )
    for text in leg.get_texts():
        text.set_color("white")
    leg.get_title().set_color("white")


    plt.tight_layout()

    # Save PNG
    plt.savefig(OUT_PNG, bbox_inches="tight")
    print(f"Saved PNG: {Path(OUT_PNG).resolve()}")

    # ----------------------------
    # Animated snowfall GIF (RESTORED)
    # ----------------------------
    rng = np.random.default_rng(123)
    snow_x = rng.uniform(0.0, 1.0, SNOW_PARTICLES)
    snow_y = rng.uniform(0.0, 1.0, SNOW_PARTICLES)
    snow_speed = rng.uniform(0.002, 0.010, SNOW_PARTICLES)
    snow_size = rng.uniform(8, 16, SNOW_PARTICLES)

    snow_artist = ax.scatter(
        snow_x, snow_y,
        transform=ax.transAxes,
        s=snow_size,
        marker="$❄$",
        color="white",
        alpha=SNOWFALL_ALPHA,
        linewidths=0,
        zorder=200,
    )

    def _update(_frame_idx: int):
        nonlocal snow_y, snow_x
        snow_y = snow_y - snow_speed
        reset = snow_y < -0.05
        snow_y[reset] = 1.05
        snow_x[reset] = rng.uniform(0.0, 1.0, reset.sum())
        snow_x = np.clip(snow_x + rng.normal(0.0, 0.0015, SNOW_PARTICLES), -0.02, 1.02)
        snow_artist.set_offsets(np.column_stack([snow_x, snow_y]))
        return (snow_artist,)

    anim = FuncAnimation(fig, _update, frames=SNOW_FRAMES, interval=SNOW_INTERVAL_MS, blit=True)

    try:
        anim.save(OUT_GIF, writer=PillowWriter(fps=18))
        print(f"Saved GIF: {Path(OUT_GIF).resolve()}")
    except Exception as e:
        warnings.warn(
            "Failed to save GIF. Make sure Pillow is installed (pip install pillow). "
            f"Error: {type(e).__name__}: {e}"
        )

    plt.show()


if __name__ == "__main__":
    main()
