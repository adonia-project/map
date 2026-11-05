# -*- coding: utf-8 -*-
"""Finalize Lurandia per user rulings (2026-11-04):
- Remove Tecala (superseded by new United Midlands)
- Extend Winnipi with the leftover southern strip of the old United Midlands
- Kalanua + Markland stay; Balboa + Sinchew growth confirmed intentional
"""
import os
import shutil
import subprocess
import geopandas as gpd
import pyogrio
from shapely import make_valid
from shapely.ops import unary_union

REPO = r"B:\02_GIT CONNECTED\map\countries\Lurandia"
DROPBOX = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\countries\Lurandia"
OLD_UM_PATH = "countries/Lurandia/Lurandia — United Midlands/Lurandia — United Midlands.gpkg"

# ---- 1. recover old United Midlands geometry from git history ----
blob = subprocess.run(
    ["git", "show", "67ab6ba^:" + OLD_UM_PATH],
    cwd=r"B:\02_GIT CONNECTED\map", capture_output=True,
).stdout
assert blob[:16] == b"SQLite format 3\x00", "did not get a GPKG blob"
tmp_old = os.path.join(REPO, "old_um_recovered.gpkg")
with open(tmp_old, "wb") as f:
    f.write(blob)
old_um_g = gpd.read_file(tmp_old, layer=pyogrio.list_layers(tmp_old)[0][0]).to_crs(4326)
old_um = unary_union([make_valid(x) for x in old_um_g.geometry])
print("old UM recovered:", round(old_um_g.to_crs(6933).area.sum() / 1e6), "km2")

# ---- 2. extend Winnipi ----
wp = os.path.join(REPO, "Lurandia — Winnipi", "Lurandia — Winnipi.gpkg")
win = gpd.read_file(wp, layer="Lurandia — Winnipi").to_crs(4326)
winnipi = unary_union([make_valid(x) for x in win.geometry])

leftover = old_um.difference(winnipi)
leftover_km2 = gpd.GeoSeries([leftover], crs=4326).to_crs(6933).area.iloc[0] / 1e6
print(f"leftover southern strip: {leftover_km2:,.0f} km2")

new_winnipi = unary_union([winnipi, make_valid(leftover)])
area = round(gpd.GeoSeries([new_winnipi], crs=4326).to_crs(6933).area.iloc[0] / 1e6, 2)
out = gpd.GeoDataFrame(
    {"Country": ["Winnipi"], "Area_km2": [area], "geometry": gpd.GeoSeries([new_winnipi], crs=4326)},
    crs=4326,
)
tmp = wp + "2.gpkg"
out.to_file(tmp, layer="Lurandia — Winnipi", driver="GPKG")
os.remove(wp)
os.replace(tmp, wp)
print(f"Winnipi extended -> {area:,.0f} km2")

# ---- 3. remove Tecala ----
for base in (REPO, DROPBOX):
    tec = os.path.join(base, "Lurandia — Tecala")
    if os.path.exists(tec):
        shutil.rmtree(tec)
        print("removed:", tec)

os.remove(tmp_old)

# ---- 4. re-mirror repo Lurandia to Dropbox ----
for d in os.listdir(REPO):
    src = os.path.join(REPO, d)
    if os.path.isdir(src):
        dst = os.path.join(DROPBOX, d)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
print("Dropbox mirror updated")

print("\nFinal Lurandia roster (17):")
for d in sorted(os.listdir(REPO)):
    if os.path.isdir(os.path.join(REPO, d)):
        print(" ", d)
