"""Harmonize Aina'akea into the canonical per-country GPKG structure.

Source: Dropbox working copy (Robinson CRS, 32 island features, name col).
Target: countries/Abyala/Abyala — Aina'akea/Abyala — Aina'akea.gpkg
        (EPSG:4326, single dissolved MultiPolygon, Country/Area_km2/geometry,
        layer name "Abyala — Aina'akea") — matching sibling Abyala GPKGs.
"""
import os
import geopandas as gpd
import pandas as pd
from shapely import make_valid
from shapely.ops import unary_union

SRC = "C:/Users/Carl/Dropbox/Adonia/QGIS Map/countries/Abyala/Abyala — Aina'akea/Aina'akea.gpkg"
DST_DIR = "countries/Abyala/Abyala — Aina'akea"
DST = os.path.join(DST_DIR, "Abyala — Aina'akea.gpkg")

g = gpd.read_file(SRC)
g = g.to_crs(4326)
geom = unary_union([make_valid(x) for x in g.geometry if x is not None])
if geom.geom_type == "GeometryCollection":
    geom = unary_union([p for p in geom.geoms if p.geom_type in ("Polygon", "MultiPolygon")])

# equal-area area (EPSG:6933 global CEA)
area_km2 = gpd.GeoSeries([geom], crs=4326).to_crs(6933).area.iloc[0] / 1e6

out = gpd.GeoDataFrame(
    {"Country": ["Aina'akea"], "Area_km2": [round(float(area_km2), 2)]},
    geometry=[geom], crs=4326,
)
os.makedirs(DST_DIR, exist_ok=True)
if os.path.exists(DST):
    os.remove(DST)
out.to_file(DST, layer="Abyala — Aina'akea", driver="GPKG")
print("wrote", DST)
print("area_km2 (equal-area):", round(float(area_km2), 1))
print("bounds4326:", [round(x, 3) for x in out.total_bounds])
print("centroid:", [round(x, 3) for x in (out.geometry.iloc[0].centroid.x, out.geometry.iloc[0].centroid.y)])
