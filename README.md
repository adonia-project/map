# Adonia QGIS Map — Folder Guide (cleaned up 2026-09-26)

## Where the countries are
**`countries/`** — THE canonical country data. One GPKG per country, named `CONTINENT — NAME.gpkg`.

| Subfolder | Countries | Notes |
|---|---|---|
| `Abyala/` | 9 | Abyala — Asikyira, Balboa, Balisca, Eberá, Haramara, Lacashe, Potocsí, Tapuya + Balisca_Fixed.gpkg |
| `Almuria/` | 2 | Almuria — Pakiak, Volistraya |
| `Arktici/` | 1 | Arktici.gpkg (polar continent, single-layer) |
| `Fosia/` | 45 | Fosia — Okaiken, Zong, Yanbaru, Nakamizu, Dagit, Vaiahi Islands, etc. |
| `Illypnia/` | 60 | Illypnia — Varkana, Breisland, Echia, Gallia, Mercia, etc. |
| `Kaftia/` | 72 | Kaftia — Alwana, Dakare, Tamazgha, Wolffrea, etc. |
| `Lurandia/` | 15 | Lurandia — Markland, Louyang, Kavik, Kawaldipa, Tecala, United Midlands, etc. |
| `Sanrobonia/` | 1 | Sanrobonia.gpkg (single-layer) |
| `Shendan_Ocean/` | 1 | Shendan_Ocean.gpkg (single-layer) |

**Total: 206 authoritative country GPKGs** (202 split from merged masters + 4 single-layer continents + Balisca_Fixed)

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
- Add new countries → create new GPKG in `countries/{Continent}/` named `CONTINENT — NAME.gpkg`
- Edit existing countries → edit the per-country GPKG directly
- After editing, refresh `adonia_countries_gpkg.zip` so the Mac stays in sync
- Old stuff → `OLD/`, never mixed into the root
