import pyogrio
import geopandas as gpd

p = "C:/Users/Carl/Dropbox/Adonia/QGIS Map/countries/Abyala/Abyala — Aina'akea/Aina'akea.gpkg"
print(pyogrio.list_layers(p))
g = gpd.read_file(p)
print('crs:', g.crs)
print('cols:', g.columns.tolist(), '| rows:', len(g))
print(g.drop(columns='geometry').to_string())
print('bounds:', [round(x, 3) for x in g.total_bounds])
utm = g.estimate_utm_crs()
print('area_km2 geom:', round(g.to_crs(utm).geometry.area.sum() / 1e6, 1))
print('valid:', bool(g.geometry.is_valid.all()))
