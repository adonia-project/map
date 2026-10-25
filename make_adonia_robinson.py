# -*- coding: utf-8 -*-
"""Robinson world map of Adonia with country labels + ellipse boundary.
Reads countries/*/*/*.gpkg (Shendan_Ocean excluded), normalizes CRS mix,
renders PNG + SVG to Dropbox (authoritative map location).
"""
import glob
import math
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd
import pyogrio
from pyproj import Transformer
from shapely import make_valid
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from adjustText import adjust_text

REPO = r"B:\02_GIT CONNECTED\map"
OUT_DIR = r"C:\Users\Carl\Dropbox\Adonia"
OUT_PNG = os.path.join(OUT_DIR, "Adonia Robinson Map.png")
OUT_SVG = os.path.join(OUT_DIR, "Adonia Robinson Map.svg")

ROBINSON = "ESRI:54030"
LAND_FILL = "#e8e4d8"
BORDER = "#4a4a4a"
OCEAN = "#cdd5da"
GRATICULE = "#b9bfc4"
LABEL = "#1a1a1a"
ELLIPSE_EDGE = "#8a9299"


def load_countries():
    paths = sorted(glob.glob(os.path.join(REPO, "countries", "*", "*", "*.gpkg")))
    frames = []
    for p in paths:
        continent = os.path.basename(os.path.dirname(os.path.dirname(p)))
        if continent == "Shendan_Ocean":
            continue
        layer = pyogrio.list_layers(p)[0][0]
        g = gpd.read_file(p, layer=layer)
        if len(g) == 0:
            continue
        if g.crs is None:
            g = g.set_crs(4326)
        g = g.to_crs(4326)
        name = str(g["Country"].iloc[0]).replace("_", " ")
        geom = unary_union([make_valid(x) for x in g.geometry if x is not None])
        if geom.geom_type == "GeometryCollection":
            geom = unary_union([x for x in geom.geoms
                                if x.geom_type in ("Polygon", "MultiPolygon")])
        frames.append(gpd.GeoDataFrame(
            {"Country": [name], "Continent": [continent]},
            geometry=[geom], crs=4326))
    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=4326)


def robinson_ellipse():
    tf = Transformer.from_crs(4326, ROBINSON, always_xy=True)
    lons, lats = [], []
    lons += list(np.linspace(-180, 180, 361)); lats += [90.0] * 361
    lons += [180.0] * 361; lats += list(np.linspace(90, -90, 361))
    lons += list(np.linspace(180, -180, 361)); lats += [-90.0] * 361
    lons += [-180.0] * 361; lats += list(np.linspace(-90, 90, 361))
    xs, ys = tf.transform(lons, lats)
    return Polygon(zip(xs, ys))


def main():
    world = load_countries()
    print(f"Loaded {len(world)} countries")
    world = world.to_crs(ROBINSON)
    world["area_km2"] = world.geometry.area / 1e6

    fig, ax = plt.subplots(figsize=(30, 16.5), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ellipse = robinson_ellipse()
    gpd.GeoSeries([ellipse], crs=ROBINSON).plot(
        ax=ax, color=OCEAN, edgecolor=ELLIPSE_EDGE, linewidth=1.2, zorder=0)

    grat_lines = []
    for lon in range(-180, 181, 30):
        grat_lines.append(LineString([(lon, -89.9), (lon, 89.9)]))
    for lat in range(-60, 61, 30):
        grat_lines.append(LineString([(-180, lat), (180, lat)]))
    grat = gpd.GeoSeries(grat_lines, crs=4326).to_crs(ROBINSON).clip(ellipse)
    grat.plot(ax=ax, color=GRATICULE, linewidth=0.4, alpha=0.7, zorder=1)

    world.plot(ax=ax, color=LAND_FILL, edgecolor=BORDER, linewidth=0.4, zorder=2)

    max_area = world["area_km2"].max()
    texts = []
    for _, row in world.iterrows():
        geom = row.geometry
        if geom.geom_type == "MultiPolygon":
            geom = max(geom.geoms, key=lambda p: p.area)
        pt = geom.representative_point()
        frac = max(row.area_km2, 1) / max_area
        fs = 2.3 + 10.7 * (math.log10(frac + 1e-4) + 4) / 4
        fs = min(max(fs, 2.3), 13)
        t = ax.text(pt.x, pt.y, row["Country"], ha="center", va="center",
                    fontsize=fs, color=LABEL, zorder=3)
        texts.append(t)

    adjust_text(texts, ax=ax,
                only_move={"text": "xy", "static": "xy", "explode": "xy", "pull": "xy"},
                expand=(1.05, 1.4), force_text=(0.2, 0.45), force_static=(0.05, 0.2),
                max_move=(8e5, 6e5), time_lim=30)
    for t in texts:
        t.set_path_effects([pe.withStroke(linewidth=1.2, foreground="#f5f2ea", alpha=0.8)])

    minx, miny, maxx, maxy = ellipse.bounds
    pad_x = (maxx - minx) * 0.015
    pad_y = (maxy - miny) * 0.03
    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)
    ax.set_axis_off()
    ax.set_title("ADONIA", fontsize=30, fontweight="bold", color="#333333",
                 family="serif", pad=18)

    fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUT_SVG, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"labeled {len(texts)} | saved:\n  {OUT_PNG}\n  {OUT_SVG}")


if __name__ == "__main__":
    main()
