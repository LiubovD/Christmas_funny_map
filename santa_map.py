"""
Holiday Santa Traditions Map (fun GIS edition)
- Color-coded Santas by tradition


Run in PyCharm. Output: santa_traditions_map.png
"""

from __future__ import annotations

import math
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Optional basemap tiles
USE_BASEMAP = True
try:
    import contextily as ctx
except Exception:
    USE_BASEMAP = False
    ctx = None


def approximate_utc_offset(lon: float) -> int:
    """
    Cartoonishly approximate timezone from longitude:
    UTC offset ~ round(lon / 15).
    (Yes, time zones are messy. That's the joke.)
    """
    return int(round(lon / 15.0))


def fmt_utc(offset: int) -> str:
    sign = "+" if offset >= 0 else "-"
    return f"UTC{sign}{abs(offset)}"


def main() -> None:
    # --- Santa traditions dataset (add/remove as you like) ---
    # name, tradition_group, place, lat, lon, note
    rows = [
        ("Santa Claus", "Nordic/Arctic", "Rovaniemi, Finland", 66.5039, 25.7294, "Tourist HQ 🎁"),
        ("Julenissen", "Nordic/Arctic", "Drobak, Norway", 59.6639, 10.6297, "Norwegian nisse vibes"),
        ("Joulupukki", "Nordic/Arctic", "Korvatunturi, Finland", 67.8333, 29.0, "Ear-fell Santa 👂⛰️"),
        ("Sinterklaas", "Western Europe", "Madrid, Spain (arrival port)", 40.4168, -3.7038, "Steamy horse logistics 🐴"),
        ("Father Christmas", "Western Europe", "London, UK", 51.5074, -0.1278, "Classic coat + cheer"),
        ("Père Noël", "Western Europe", "Strasbourg, France", 48.5734, 7.7521, "Markets + magic ✨"),
        ("La Befana", "Mediterranean", "Urbania, Italy", 43.6676, 12.3744, "Broom-based delivery 🧹"),
        ("Three Kings", "Mediterranean", "Seville, Spain", 37.3891, -5.9845, "Epiphany parade 👑"),
        ("Ded Moroz (Father Frost)", "Slavic", "Veliky Ustyug, Russia", 60.7619, 46.3056, "Residence of Father Frost ❄️🇷🇺"),
        ("Snegurochka", "Slavic", "Kostroma, Russia", 57.7665, 40.9269, "Co-pilot: Snow Maiden 🧊"),
        ("Santa (US Pop Culture)", "Americas", "New York City, USA", 40.7128, -74.0060, "Sleigh traffic is real 🛷"),
        ("Papai Noel", "Americas", "Rio de Janeiro, Brazil", -22.9068, -43.1729, "Tropical Santa = short sleeves 😅"),
        ("Santa (AUS Summer Mode)", "Oceania", "Sydney, Australia", -33.8688, 151.2093, "BBQ reindeer 🦌🔥"),
        ("Santa (NZ)", "Oceania", "Auckland, New Zealand", -36.8485, 174.7633, "First to unwrap (roughly) 🎉"),
        ("Hoteiosho", "East Asia", "Tokyo, Japan", 35.6762, 139.6503, "One eye open until you’re good 👀"),
    ]

    df = pd.DataFrame(rows, columns=["name", "tradition", "place", "lat", "lon", "note"])
    df["utc"] = df["lon"].apply(lambda x: fmt_utc(approximate_utc_offset(x)))

    # Geometry in WGS84
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["lon"], df["lat"])],
        crs="EPSG:4326",
    )

    # Project to Web Mercator for basemap + metric buffers
    gdf_3857 = gdf.to_crs(epsg=3857)

    # Create playful buffers (~300 km) to look like "delivery influence zones"
    buffer_m = 300_000
    buffers = gdf_3857.copy()
    buffers["geometry"] = buffers.geometry.buffer(buffer_m)

    # --- Styling: color-code by tradition ---
    traditions = sorted(gdf_3857["tradition"].unique())
    cmap = plt.get_cmap("tab10")
    color_map = {t: cmap(i % 10) for i, t in enumerate(traditions)}

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_title("Holiday Santa Traditions Map 🎅🌍 (CRS-aware-ish)", fontsize=18, pad=16)

    # buffers (transparent)
    for t in traditions:
        buffers[buffers["tradition"] == t].plot(
            ax=ax,
            color=color_map[t],
            alpha=0.12,
            linewidth=0,
        )

    # points
    for t in traditions:
        gdf_3857[gdf_3857["tradition"] == t].plot(
            ax=ax,
            color=color_map[t],
            markersize=70,
            label=t,
            edgecolor="black",
            linewidth=0.6,
            alpha=0.95,
        )

    # basemap
    if USE_BASEMAP and ctx is not None:
        try:
            ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
        except Exception:
            # If tiles fail, continue without basemap
            pass

    # labels + playful notes
    for _, r in gdf_3857.iterrows():
        x, y = r.geometry.x, r.geometry.y
        label = f"{r['name']}\n{r['place']} • {r['utc']}"
        ax.annotate(
            label,
            (x, y),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.75),
        )

    # --- CRS jokes / map annotations ---
    # North Pole joke point (approx, then projected)
    north_pole = gpd.GeoSeries([Point(0, 90)], crs="EPSG:4326").to_crs(epsg=3857).iloc[0]
    ax.annotate(
        "⚠️ North Pole: geometry may be undefined\nin Web Mercator. Santa does not care.",
        (north_pole.x, north_pole.y),
        xytext=(20, -40),
        textcoords="offset points",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.35", fc="lemonchiffon", ec="goldenrod", alpha=0.9),
        arrowprops=dict(arrowstyle="->", lw=1.2),
    )

    ax.text(
        0.02,
        0.02,
        "CRS confession: plotted in EPSG:3857 because tiles demanded it.\n"
        "Accuracy: festive. Buffers: emotional (300 km). Time zones: vibe-based.\n"
        "🎄 Merry Christmas & a correctly georeferenced New Year!",
        transform=ax.transAxes,
        fontsize=10.5,
        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="lightgray", alpha=0.85),
        va="bottom",
        ha="left",
    )

    # layout & legend
    ax.set_axis_off()
    ax.legend(
        loc="upper left",
        frameon=True,
        framealpha=0.9,
        title="Tradition",
        fontsize=10,
        title_fontsize=11,
    )

    out = "santa_traditions_map.png"
    plt.tight_layout()
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.show()

    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
