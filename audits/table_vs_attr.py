# -*- coding: utf-8 -*-
"""Compare continent article table areas vs GPKG attribute vs measured geometry. v2"""
import json, io, re, urllib.request, urllib.parse
import geopandas as gpd, glob, os, warnings
warnings.filterwarnings("ignore")
UA = "Takeru-Sync/1.0 (Letta Code; talod.miraheze.org)"
API = "https://talod.miraheze.org/w/api.php"
def pull(title):
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(
        {"action":"query","prop":"revisions","titles":title,"rvprop":"ids|content","format":"json"}),
        headers={"User-Agent": UA})
    r = json.loads(urllib.request.urlopen(req).read().decode())
    p = list(r["query"]["pages"].values())[0]
    return p["revisions"][0]["revid"], p["revisions"][0]["*"]

numre = re.compile(r"^[\d,]+(\.\d+)?$")
def table_areas(text):
    out = {}
    for line in text.split("\n"):
        if "{{flag|" not in line: continue
        cells = [c.strip() for c in line.split("||")]
        name = None
        for c in cells:
            m = re.match(r"^\[\[([^\]|]+)\]\]$", c)
            if m and not m.group(1).startswith("File:"):
                name = m.group(1).strip(); break
        if not name: continue
        seen_name = False
        for c in cells:
            if name is not None and c == "[[%s]]" % name: seen_name = True; continue
            if not seen_name: continue
            cc = c.replace("{{formatnum:","").replace("}}","")
            if numre.match(cc) and len(cc.replace(",","").replace(".","")) >= 3:
                out[name] = float(cc.replace(",","")); break
    return out

tables = {}
for cont in ("Kaftia","Illypnia","Abyala","Lurandia","Fosia","Almuria","Shendan_Ocean","Arktici"):
    try:
        rev, text = pull(cont)
        ta = table_areas(text)
        tables[cont] = ta
        print("%-14s rev %s: %d rows w/ areas" % (cont, rev, len(ta)))
    except Exception as e:
        print(cont, "ERR", e)

audit = {}
for p in sorted(glob.glob(r"countries\*\*\*.gpkg")):
    name = os.path.basename(p).replace(".gpkg","")
    cont, _, cname = name.partition(" — ")
    try:
        g = gpd.read_file(p)
        attr = None
        for col in g.columns:
            if col.lower() == "area_km2": attr = float(g[col].sum()); break
        g4 = g.to_crs(4326); geom = g4.geometry.union_all(); c = geom.centroid
        laea = "+proj=laea +lat_0=%.6f +lon_0=%.6f +datum=WGS84 +units=m +no_defs" % (c.y, c.x)
        meas = g4.to_crs(laea).geometry.area.sum()/1e6
        audit[(cont, cname)] = (attr, meas)
    except Exception:
        audit[(cont, cname)] = (None, None)

rows = []
for cont, ta in tables.items():
    for cname, tarea in sorted(ta.items()):
        key = (cont, cname)
        attr, meas = audit.get(key, (None, None))
        if attr is None:
            d = None; tag = "NO_ATTR"
        else:
            d = (attr - tarea)/tarea*100
            tag = "OK" if abs(d) < 0.5 else ("DRIFT" if abs(d) < 2 else "STALE")
        dm = None if meas is None or not tarea else (meas - tarea)/tarea*100
        rows.append((cont, cname, tarea, attr, meas, d, dm, tag))

with io.open(r"audits\table_vs_attr_20261024.csv","w",encoding="utf-8",newline="\n") as f:
    f.write("continent,country,table_km2,attr_km2,measured_km2,attr_vs_table_pct,meas_vs_table_pct,status\n")
    for r in rows:
        f.write(",".join("" if v is None else (("%.2f" % v) if isinstance(v,float) else str(v)) for v in r) + "\n")

ok = [r for r in rows if r[7]=="OK"]; bad = [r for r in rows if r[7] not in ("OK",)]
print()
print("rows compared: %d | attr matches table: %d | mismatch: %d" % (len(rows), len(ok), len(bad)))
print()
print("%-12s %-22s %13s %13s %13s %8s %8s" % ("continent","country","table","attr","measured","attr%","meas%"))
for r in sorted(bad, key=lambda r: -(abs(r[5]) if r[5] is not None else 999)):
    print("%-12s %-22s %13.1f %13s %13s %8s %8s %s" % (r[0], r[1], r[2],
        ("%.1f" % r[3]) if r[3] is not None else "-",
        ("%.1f" % r[4]) if r[4] is not None else "-",
        ("%+.2f" % r[5]) if r[5] is not None else "-",
        ("%+.2f" % r[6]) if r[6] is not None else "-", r[7]))
