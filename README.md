# Adonia QGIS Map — Folder Guide (cleaned up 2026-09-26, git-connected 2026-09-27)

**GitHub:** https://github.com/adonia-project/map (branch `main`)

## Where the countries are
**`countries/`** — THE canonical country data. **One folder per country**, each containing its GPKG: `countries/{Continent}/{Continent — Country}/{Continent — Country}.gpkg`

Country folders are the workspace for everything about that country — drop renders, layouts, and exports alongside the GPKG as you build individual maps.

| Subfolder | Countries | Notes |
|---|---|---|
| `Abyala/` | 8 | Asikyira, Balboa, Balisca, Eberá, Haramara, Lacashe, Potocsí, Tapuya |
| `Almuria/` | 2 | Pakiak, Volistraya |
| `Arktici/` | 1 | Arktici (polar continent, single-layer) |
| `Fosia/` | 45 | Okaiken, Zong, Yanbaru, Nakamizu, Dagit, Vaiahi Islands, etc. |
| `Illypnia/` | 60 | Varkana, Breisland, Echia, Gallia, Mercia, etc. |
| `Kaftia/` | 72 | Alwana, Dakare, Tamazgha, Wolffrea, etc. |
| `Lurandia/` | 15 | Markland, Louyang, Kavik, Kawaldipa, Tecala, United Midlands, etc. |
| `Sanrobonia/` | 1 | Sanrobonia (single-layer) |
| `Shendan_Ocean/` | 1 | Shendan_Ocean (single-layer) |

**Total: 205 authoritative country GPKGs**, each in its own folder.

## Other active files (root)
- `ADONIA QGIS.qgz` — main QGIS project (Windows). Layers reference the canonical GPKGs in `countries/`.
- `ADONIA QGIS - MAC REFERENCE.qgz` — Mac-side project for reference.
- `ADONIA_SAFE_EDIT.gdb` — continental outlines layer (adonia_2026, Robinson CRS) — **referenced by the main project, do not delete**.
- `Cities in Adonia.shp` — city points layer.
- `adonia_countries_gpkg.zip` — snapshot of the canonical `countries/` data (Mac sync, 2026-09-26).
- `load_adonia_countries.py` — QGIS Python console script that loads all `countries/` GPKGs into an "Adonia Countries" layer group. Auto-detects Windows vs Mac paths.
- `split_countries.py` — utility script used to split the old merged GPKGs into per-country files.

## OLD/ — archived superseded data (safe to ignore, do not delete)
- `countries_20260905/` — older Sep 5 version of the countries folder
- `Adonia Countries.gdb` — old master country GDB (Mar 2026, superseded)
- `Abyala.gpkg`, `Almuria.gpkg`, `Fosia.gpkg`, `Illypnia.gpkg`, `Kaftia.gpkg`, `Lurandia.gpkg` — old merged continent GPKGs (now split into per-country files)
- `ADONIA EDIT THIS.gpkg` — Mar 5 working copy, superseded
- `Adonia 2026 Shape File*` (3 sets) — Feb 2026 original shapefiles + REHASHED + TEMP NO HOLES variants
- `Location of New Country/` — Mar 2026 georeferencing experiments
- Misc: `DATA SAVE .csv`, `.qmd` style files, stray `.aux.xml`/`.points` files

## Rule of thumb going forward
- Add new countries → new folder `countries/{Continent}/{Continent — Name}/` with the GPKG inside
- Edit existing countries → edit the GPKG in its country folder; per-country map assets (renders, layouts, exports) go in the same folder
- Commit + push when done: `git add -A && git commit -m "..." && git push`
- Old stuff → `OLD/` (gitignored), never mixed into the root
- The Mac syncs via the `adonia_countries_gpkg.zip` snapshot (gitignored) — refresh it after big changes
