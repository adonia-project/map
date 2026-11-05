import os
import pyogrio
import geopandas as gpd
from shapely import make_valid
from shapely.ops import unary_union

SHUB = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\GIS.gpkg"
REPO = r"B:\02_GIT CONNECTED\map\countries\Lurandia"

def u(g):
    return unary_union([make_valid(x) for x in g.geometry if x is not None])

shub = gpd.read_file(SHUB, layer="countries").to_crs(4326)
geoms = {name: u(grp) for name, grp in shub.groupby("Country")}

def repo_geom(name):
    p = os.path.join(REPO, f"Lurandia — {name}", f"Lurandia — {name}.gpkg")
    g = gpd.read_file(p, layer=pyogrio.list_layers(p)[0][0]).to_crs(4326)
    return u(g)

old_um = repo_geom("United Midlands")
winnipi = geoms["Winnipi"]
inter = old_um.intersection(winnipi).area
iou = inter / old_um.union(winnipi).area
print(f"Winnipi vs OLD United Midlands: IoU = {iou:.3f} | "
      f"Winnipi inside old UM: {winnipi.intersection(old_um).area / winnipi.area:.2%}")

new_um = geoms["United Midlands"]
print(f"New UM inside old UM: {new_um.intersection(old_um).area / new_um.area:.2%}")
print(f"New UM overlaps Winnipi: {new_um.intersection(winnipi).area / 1000:.0f} thousand deg2")

kavik = repo_geom("Kavik")
print("\nKavik vs Shub countries (overlap fraction of Kavik):")
for name, g in geoms.items():
    ov = kavik.intersection(g).area / kavik.area
    if ov > 0.001:
        print(f"  {name}: {ov:.2%}")
print("  (none listed = no overlap)")

print("\nShub countries mutual overlaps (should be ~0):")
names = list(geoms)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        ov = geoms[names[i]].intersection(geoms[names[j]]).area
        if ov > 0.01:
            print(f"  {names[i]} <-> {names[j]}: {ov:.4f} deg2")
print("done")
