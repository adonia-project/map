# -*- coding: utf-8 -*-
"""
Split continent GPKGs into one GPKG per country: countries/{Continent}/{Continent} - {Name}.gpkg
Preserves native CRS, attributes, and geometry exactly. Skips layer_styles tables.
"""
import os
import re
import sqlite3
import subprocess
import sys

# force UTF-8 output on Windows console
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# GDAL environment (required for ogr2ogr on Windows)
os.environ["GDAL_DATA"] = r"C:\OSGeo4W\apps\gdal\share\gdal"
os.environ["PROJ_LIB"] = r"C:\OSGeo4W\share\proj"

BASE = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\countries"
OGR2OGR = r"C:\OSGeo4W\bin\ogr2ogr.exe"
DASH = u"\u2014"  # em dash

def clean_name(raw):
    m = re.match(u"^[A-Za-z_]+\\s*[\u2014\\-]\\s*(.+)$", raw)
    name = m.group(1) if m else raw
    name = name.replace("_", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name

def split_gpkg(gpkg_path, continent, out_dir):
    conn = sqlite3.connect(gpkg_path)
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM gpkg_contents WHERE data_type='features'")
    tables = [r[0] for r in cur.fetchall()]
    conn.close()

    made, failed = [], []
    for t in tables:
        if t == "layer_styles":
            continue
        name = clean_name(t)
        out_name = u"{} {} {}".format(continent, DASH, name)
        out_path = os.path.join(out_dir, out_name + u".gpkg")
        if os.path.exists(out_path):
            os.remove(out_path)
        r = subprocess.run([OGR2OGR, "-f", "GPKG", out_path, gpkg_path, t],
                           capture_output=True)
        if r.returncode != 0:
            failed.append(out_name)
            sys.stderr.write(u"FAILED {}: {}\n".format(out_name, r.stderr.decode("utf-8", "replace")[:200]))
        else:
            made.append(out_name)
    return made, failed

total, all_failed = 0, []
for continent in sorted(os.listdir(BASE)):
    cdir = os.path.join(BASE, continent)
    if not os.path.isdir(cdir):
        continue
    for f in sorted(os.listdir(cdir)):
        if not f.lower().endswith(".gpkg") or f.endswith(".bak"):
            continue
        stem = os.path.splitext(f)[0]
        is_master = stem.lower() == continent.lower()
        conn = sqlite3.connect(os.path.join(cdir, f))
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM gpkg_contents WHERE data_type='features'")
        nfeat = cur.fetchone()[0]
        conn.close()
        if is_master and nfeat > 1:
            print(u"Splitting {} ({} layers)".format(f, nfeat))
            made, failed = split_gpkg(os.path.join(cdir, f), continent, cdir)
            print(u"  -> {} country gpkgs, {} failed".format(len(made), len(failed)))
            total += len(made)
            all_failed += failed
        elif is_master and nfeat == 1:
            print(u"Keeping single-layer master: {}".format(f))

print(u"\nTotal country GPKGs created: {}".format(total))
if all_failed:
    print(u"Failed: " + u", ".join(all_failed))
