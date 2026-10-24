# -*- coding: utf-8 -*-
"""Batch audit v2: Area_km2 attribute vs geometry (LAEA about WGS84 centroid)."""
import geopandas as gpd, glob, io, os, warnings
warnings.filterwarnings("ignore")

rows = []
files = sorted(glob.glob(r"countries\*\*\*.gpkg"))
for p in files:
    name = os.path.basename(p).replace(".gpkg", "")
    try:
        g = gpd.read_file(p)
        if len(g) == 0:
            rows.append((name, None, None, None, "EMPTY")); continue
        attr = None
        for col in g.columns:
            if col.lower() == "area_km2":
                attr = float(g[col].sum()); break
        if attr is None:
            rows.append((name, None, None, None, "NO_AREA_COL:" + ",".join(g.columns.tolist())[:60])); continue
        g4 = g.to_crs(4326)
        geom = g4.geometry.union_all()
        c = geom.centroid
        laea = "+proj=laea +lat_0=%.6f +lon_0=%.6f +datum=WGS84 +units=m +no_defs" % (c.y, c.x)
        meas = g4.to_crs(laea).geometry.area.sum() / 1e6
        delta = (attr - meas) / meas * 100.0
        flag = "OK" if abs(delta) < 0.5 else ("DRIFT" if abs(delta) < 2 else "STALE")
        rows.append((name, attr, round(meas, 2), round(delta, 2), flag))
    except Exception as e:
        rows.append((name, None, None, None, "ERR:" + repr(e)[:70]))

with io.open(r"audits\area_attribute_audit_20261024.csv", "w", encoding="utf-8", newline="\n") as f:
    f.write("country,attribute_km2,measured_km2,delta_pct,status\n")
    for r in rows:
        f.write(",".join("" if v is None else str(v) for v in r) + "\n")

ok = [r for r in rows if r[4] == "OK"]
drift = [r for r in rows if r[4] == "DRIFT"]
stale = [r for r in rows if r[4] == "STALE"]
other = [r for r in rows if r[4] not in ("OK", "DRIFT", "STALE")]
print("total: %d | OK: %d | DRIFT(0.5-2%%): %d | STALE(>2%%): %d | other: %d" % (len(rows), len(ok), len(drift), len(stale), len(other)))
print()
print("=== STALE (>2% off) ===")
for r in sorted(stale, key=lambda r: -abs(r[3])):
    print("  %-40s attr=%15.2f meas=%15.2f delta=%+7.2f%%" % (r[0], r[1], r[2], r[3]))
print()
print("=== DRIFT (0.5-2%) ===")
for r in sorted(drift, key=lambda r: -abs(r[3])):
    print("  %-40s attr=%15.2f meas=%15.2f delta=%+7.2f%%" % (r[0], r[1], r[2], r[3]))
print()
print("=== OTHER (no col / empty / err) ===")
for r in other:
    print("  %-40s %s" % (r[0], r[4]))
