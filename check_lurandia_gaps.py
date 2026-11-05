import os
import geopandas as gpd
import pyogrio
from shapely import make_valid
from shapely.ops import unary_union

REPO = r"B:\02_GIT CONNECTED\map\countries\Lurandia"

def repo_geom(name):
    p = os.path.join(REPO, f"Lurandia — {name}", f"Lurandia — {name}.gpkg")
    g = gpd.read_file(p, layer=pyogrio.list_layers(p)[0][0]).to_crs(4326)
    return unary_union([make_valid(x) for x in g.geometry])

repo_only = ["Kalanua", "Markland", "Tecala"]
shub_new = ["Amiera", "Balboa", "Etawa", "Sinchew", "United Midlands", "Winnipi"]

for r in repo_only:
    rg = repo_geom(r)
    for s in shub_new:
        sg = repo_geom(s)
        ov = rg.intersection(sg).area
        if ov > 0.01:
            frac = ov / rg.area
            print(f"OVERLAP: {r} <-> {s}: {ov:.4f} deg2 ({frac:.1%} of {r})")
print("overlap check done")
