# Adonia Countries Loader v4 — LOCAL, no gdal
# Run in the QGIS Python Console SCRIPT EDITOR (not the interactive prompt):
# Plugins > Python Console > Show Editor (paper icon) > Open this file > Run

import os
import platform
from qgis.core import QgsVectorLayer, QgsProject, QgsProviderRegistry

# Auto-detect: Windows (Dropbox) or Mac (Documents) — both hold the same countries/ folder
if platform.system() == "Windows" or os.path.isdir(r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\countries"):
    COUNTRIES_DIR = r"C:\Users\Carl\Dropbox\Adonia\QGIS Map\countries"
else:
    COUNTRIES_DIR = "/Users/user/Documents/wiki/maps/countries"

project = QgsProject.instance()
root = project.layerTreeRoot()

existing = root.findGroup("Adonia Countries")
if existing:
    root.removeChildNode(existing)

master_group = root.addGroup("Adonia Countries")

reg = QgsProviderRegistry.instance()
md = reg.providerMetadata("ogr")

total = 0
for entry in sorted(os.listdir(COUNTRIES_DIR)):
    subdir = os.path.join(COUNTRIES_DIR, entry)
    if not os.path.isdir(subdir):
        continue

    gpkgs = [f for f in os.listdir(subdir)
             if f.lower().endswith(".gpkg") and not f.endswith(".bak")]
    if not gpkgs:
        continue

    # Prefer the continent-named GPKG (e.g. "Lurandia.gpkg" in "Lurandia/")
    continent_gpkg = [f for f in gpkgs if os.path.splitext(f)[0].lower() == entry.lower()]
    gpkg_path = os.path.join(subdir, continent_gpkg[0] if continent_gpkg else sorted(gpkgs)[0])
    cont_group = master_group.addGroup(entry.replace("_", " "))

    count = 0
    for layer_md in md.querySublayers(gpkg_path):
        opts = QgsVectorLayer.LayerOptions()
        opts.loadDefaultStyle = False
        layer = QgsVectorLayer(layer_md.uri(),
                               layer_md.name().replace("_", " "),
                               "ogr", opts)
        if layer.isValid():
            project.addMapLayer(layer, False)
            cont_group.addLayer(layer)
            count += 1
            total += 1

    print(f"{entry}: {count} layers loaded")

print(f"\nDone — {total} country layers loaded")
