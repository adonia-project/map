# -*- coding: utf-8 -*-
"""Location of Aina'akea.png — orthographic globe, house style.
Grey ocean gradient, flat #c8c8c8 land, #3f8f4f highlight, subtle graticule.
Adapted from make_louyang_globe.py.
"""
import glob
import math
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PolyCollection

TARGET = "Aina'akea"
CENTER_LON, CENTER_LAT = -160.47, 37.53  # Aina'akea centroid
OUT = r'B:\02_GIT CONNECTED\map\Location of Aina''akea.png'.replace("''", "'")

files = glob.glob(r'B:\02_GIT CONNECTED\map\countries\*\*\*.gpkg') + \
        glob.glob(r'B:\02_GIT CONNECTED\map\countries\*\*.gpkg')
frames = []
for f in files:
    try:
        g = gpd.read_file(f)
        if 'Country' in g.columns and len(g):
            frames.append(g[['Country', 'geometry']].to_crs(4326))
    except Exception:
        pass
world = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=4326)

lon0, lat0 = math.radians(CENTER_LON), math.radians(CENTER_LAT)

def visible_z(lon, lat):
    return math.sin(lat0)*math.sin(lat) + math.cos(lat0)*math.cos(lat)*math.cos(lon - lon0)

def slerp_crossing(a, b):
    def to3(la, lo):
        return np.array([math.cos(la)*math.cos(lo), math.cos(la)*math.sin(lo), math.sin(la)])
    va, vb = to3(*a), to3(*b)
    fa, fb = visible_z(a[1], a[0]), visible_z(b[1], b[0])
    t = fa / (fa - fb)
    v = va*(1-t) + vb*t
    v /= np.linalg.norm(v)
    return (math.asin(v[2]), math.atan2(v[1], v[0]))

def clip_ring(coords):
    pts = [(math.radians(lo), math.radians(la)) for lo, la in coords]
    out = []
    n = len(pts)
    started = False
    for i in range(n):
        a = pts[i]; b = pts[(i+1) % n]
        za = visible_z(a[0], a[1]); zb = visible_z(b[0], b[1])
        if za >= 0:
            out.append(a); started = True
            if zb < 0:
                c = slerp_crossing((a[1], a[0]), (b[1], b[0]))
                out.append((c[1], c[0]))
        else:
            if zb >= 0 and started:
                c = slerp_crossing((b[1], b[0]), (a[1], a[0]))
                out.append((c[1], c[0]))
    if len(out) < 3:
        return None
    return out

def project(lon, lat):
    x = math.cos(lat)*math.sin(lon - lon0)
    y = math.cos(lat0)*math.sin(lat) - math.sin(lat0)*math.cos(lat)*math.cos(lon - lon0)
    if not (math.isfinite(x) and math.isfinite(y)):
        return None
    return x, y

def render_geom(geom):
    polys = geom.geoms if geom.geom_type == 'MultiPolygon' else [geom]
    for poly in polys:
        for ring in [poly.exterior]:
            coords = [(math.degrees(p[0]), math.degrees(p[1])) for p in
                      (clip_ring(ring.coords) or [])]
            if len(coords) < 3:
                continue
            proj = [project(math.radians(lo), math.radians(la)) for lo, la in coords]
            proj = [p for p in proj if p]
            if len(proj) >= 3:
                yield proj

fig, ax = plt.subplots(figsize=(8, 8), dpi=250)
ax.set_xlim(-1.02, 1.02); ax.set_ylim(-1.02, 1.02)
ax.set_aspect('equal'); ax.axis('off')
fig.patch.set_alpha(0)

r = np.linspace(0, 1, 256)
for i in range(255, -1, -1):
    ax.add_patch(Circle((0, 0), r[i], color='#f0f0f0' if i > 4 else 'white', zorder=0))
ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor='#c6c6c6', lw=0.8, zorder=10))

for g_lon in range(-180, 181, 10):
    lats = np.linspace(-90, 90, 361)
    z = np.array([visible_z(math.radians(g_lon), math.radians(la)) for la in lats])
    xs = np.array([project(math.radians(g_lon), math.radians(la))[0] for la in lats])
    ys = np.array([project(math.radians(g_lon), math.radians(la))[1] for la in lats])
    xs = np.where(z >= 0, xs, np.nan); ys = np.where(z >= 0, ys, np.nan)
    ax.plot(xs, ys, color='#d3d6d9', lw=0.25, alpha=0.8, zorder=1)
for g_lat in range(-80, 81, 10):
    lons = np.linspace(-180, 180, 721)
    z = np.array([visible_z(math.radians(lo), math.radians(g_lat)) for lo in lons])
    xs = np.array([project(math.radians(lo), math.radians(g_lat))[0] for lo in lons])
    ys = np.array([project(math.radians(lo), math.radians(g_lat))[1] for lo in lons])
    xs = np.where(z >= 0, xs, np.nan); ys = np.where(z >= 0, ys, np.nan)
    ax.plot(xs, ys, color='#d3d6d9', lw=0.25, alpha=0.8, zorder=1)

target_polys, land_polys = [], []
for _, row in world.iterrows():
    for coords in render_geom(row.geometry):
        if row.Country == TARGET:
            target_polys.append(coords)
        else:
            land_polys.append(coords)
ax.add_collection(PolyCollection(land_polys, facecolor='#c8c8c8', edgecolor='none', zorder=2))
ax.add_collection(PolyCollection(target_polys, facecolor='#3f8f4f', edgecolor='none', zorder=3))

fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
fig.savefig(OUT, dpi=250, transparent=True)
print('saved', OUT, '| target polys:', len(target_polys), '| land polys:', len(land_polys))
