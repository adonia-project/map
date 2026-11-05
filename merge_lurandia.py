# -*- coding: utf-8 -*-
"""Merge Shub's Lurandia package into canonical per-country GPKGs.

Shub's package (Dropbox QGIS Map/GIS.gpkg) takes precedence for all countries
it contains EXCEPT Kaneda and Kavik (repo versions stay).
Old United Midlands geometry is replaced by the new smaller northern UM;
Winnipi is created as a new country.
Kalanua, Markland, Tecala are NOT in Shub's package and are left untouched
(pending user decision).
"""
import os
import shutil
import geopandas as gpd
import pyogrio
from shapely import make_valid
from shapely.ops import unary_union

SHUB = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\GIS.gpkg"
REPO = r"B:\02_GIT CONNECTED\map\countries\Lurandia"
DROPBOX = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\countries\Lurandia"

KEEP_REPO = {"Kaneda", "Kavik"}

shub = gpd.read_file(SHUB, layer="countries")

for name, grp in shub.groupby("Country"):
    if name in KEEP_REPO:
        print(f"skip (repo version stays): {name}")
        continue
    geom = unary_union([make_valid(x) for x in grp.geometry if x is not None])
    one = gpd.GeoSeries([geom], crs=grp.crs)
    area = round(one.to_crs(6933).area.iloc[0] / 1e6, 2)
    out = gpd.GeoDataFrame(
        {"Country": [name], "Area_km2": [area], "geometry": one},
        crs=grp.crs,
    ).to_crs(4326)

    folder = os.path.join(REPO, f"Lurandia — {name}")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"Lurandia — {name}.gpkg")
    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    out.to_file(tmp, layer=f"Lurandia — {name}", driver="GPKG")
    if os.path.exists(path):
        os.remove(path)
    os.replace(tmp, path)
    print(f"wrote: Lurandia — {name}  ({area:,.0f} km2)")

print("\nmirroring to Dropbox working copy...")
for d in os.listdir(REPO):
    src = os.path.join(REPO, d)
    if os.path.isdir(src):
        dst = os.path.join(DROPBOX, d)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
print("mirror done")

print("\nFinal Lurandia roster:")
for d in sorted(os.listdir(REPO)):
    if os.path.isdir(os.path.join(REPO, d)):
        print(" ", d)
