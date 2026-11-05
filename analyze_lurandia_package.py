import glob
import os
import pyogrio
import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.ops import unary_union

SHUB = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\GIS.gpkg"
REPO = r"B:\02_GIT CONNECTED\map\countries\Lurandia"

def dissolve_area(g):
    geom = unary_union([make_valid(x) for x in g.geometry if x is not None])
    return gpd.GeoSeries([geom], crs=g.crs).to_crs(6933).area.iloc[0] / 1e6

def centroid(g):
    geom = unary_union([make_valid(x) for x in g.geometry if x is not None])
    c = gpd.GeoSeries([geom], crs=g.crs).to_crs(4326).centroid.iloc[0]
    return round(c.y, 2), round(c.x, 2)

shub = gpd.read_file(SHUB, layer="countries")
print("=== SHUB PACKAGE (per-country) ===")
rows = []
for name, grp in shub.groupby("Country"):
    a = dissolve_area(grp)
    cy, cx = centroid(grp)
    attr = grp["Area_km2"].iloc[0]
    rows.append((name, len(grp), round(a), attr, cy, cx))
df = pd.DataFrame(rows, columns=["Country", "feats", "area_eq_km2", "attr_Area_km2", "lat", "lon"])
print(df.to_string(index=False))

print("\n=== REPO LURANDIA (current) ===")
rows = []
for p in glob.glob(os.path.join(REPO, "*", "*.gpkg")):
    layer = pyogrio.list_layers(p)[0][0]
    g = gpd.read_file(p, layer=layer)
    name = str(g["Country"].iloc[0]).replace("_", " ")
    rows.append((name, len(g), round(dissolve_area(g)), centroid(g)))
print(pd.DataFrame(rows, columns=["Country", "feats", "area_eq_km2", "centroid"]).to_string(index=False))

print("\n=== GEOMETRY DIFF CHECK (countries in both) ===")
repo_names = {r[0] for r in rows}
for name, grp in shub.groupby("Country"):
    if name in repo_names:
        p = os.path.join(REPO, f"Lurandia — {name}", f"Lurandia — {name}.gpkg")
        layer = pyogrio.list_layers(p)[0][0]
        old = gpd.read_file(p, layer=layer).to_crs(4326)
        new = grp.to_crs(4326)
        old_u = unary_union([make_valid(x) for x in old.geometry])
        new_u = unary_union([make_valid(x) for x in new.geometry])
        inter = old_u.intersection(new_u).area
        union = old_u.union(new_u).area
        iou = inter / union if union else 0
        print(f"  {name:18s} IoU old-vs-new: {iou:.3f}  (1.0 = identical)")
