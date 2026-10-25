# -*- coding: utf-8 -*-
"""Blank equal-area (Mollweide) world map of Adonia - no labels, no captions.
Reads countries/*/*/*.gpkg, normalizes CRS mix, renders PNG to map repo + Dropbox.
"""
import glob
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyogrio
from pyproj import Transformer
from shapely import make_valid
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

REPO = r"B:\02_GIT CONNECTED\map"
OUT_PNG = os.path.join(REPO, "Adonia blank map.png")
OUT_PNG_DBX = r"C:\Users\Carl\Dropbox\Adonia\Adonia blank map.png"

MOLLWEIDE = "+proj=moll +lon_0=0 +x_0=0 +y_0=0"
LAND_FILL = "#e8e4d8"
BORDER = "#4a4a4a"
OCEAN = "#cdd5da"
GRATICULE = "#b9bfc4"
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


def mollweide_ellipse():
    tf = Transformer.from_crs(4326, MOLLWEIDE, always_xy=True)
    lons, lats = [], []
    lons += list(np.linspace(-180, 180, 361)); lats += [90.0] * 361
    lons += [180.0] * 361; lats += list(np.linspace(90, -90, 361))
    lons += list(np.linspace(180, -180, 361)); lats += [-90.0] * 361
    lons += [-180.0] * 361; lats += list(np.linspace(-90, 90, 361))
    xs, ys = tf.transform(lons, lats)
    return Polygon(zip(xs, ys))


def main():
    world = load_countries()
    print("Loaded %d countries" % len(world))
    world = world.to_crs(MOLLWEIDE)

    fig, ax = plt.subplots(figsize=(20, 10.4), dpi=200)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ellipse = mollweide_ellipse()
    gpd.GeoSeries([ellipse], crs=MOLLWEIDE).plot(
        ax=ax, color=OCEAN, edgecolor=ELLIPSE_EDGE, linewidth=1.2, zorder=0)

    grat_lines = []
    for lon in range(-180, 181, 30):
        grat_lines.append(LineString([(lon, -89.9), (lon, 89.9)]))
    for lat in range(-60, 61, 30):
        grat_lines.append(LineString([(-180, lat), (180, lat)]))
    grat = gpd.GeoSeries(grat_lines, crs=4326).to_crs(MOLLWEIDE).clip(ellipse)
    grat.plot(ax=ax, color=GRATICULE, linewidth=0.4, alpha=0.7, zorder=1)

    world.plot(ax=ax, color=LAND_FILL, edgecolor=BORDER, linewidth=0.45, zorder=2)

    minx, miny, maxx, maxy = ellipse.bounds
    pad_x = (maxx - minx) * 0.015
    pad_y = (maxy - miny) * 0.03
    ax.set_xlim(minx - pad_x, maxx + pad_x)
    ax.set_ylim(miny - pad_y, maxy + pad_y)
    ax.set_axis_off()

    fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUT_PNG_DBX, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    from PIL import Image
    im = Image.open(OUT_PNG)
    print("saved: %s (%dx%d)" % (OUT_PNG, im.size[0], im.size[1]))


if __name__ == "__main__":
    main()
