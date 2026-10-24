# Area Attribute Audit — 2026-10-24

Method: every per-country GPKG (205) measured via Lambert Azimuthal Equal-Area about
its WGS84 centroid; `Area_km2` attribute and continent-article table value compared
against the measurement. Tables are the wiki canon authority.

## Verdict
- **Continent article tables = healthy.** They match measured geometry within ~0.3%
  almost everywhere (they were computed correctly from the shapefiles).
- **GPKG `Area_km2` attributes = the stale side.** 83 of 203 compared rows mismatch.

## Files
- `area_attribute_audit_20261024.csv` — attribute vs geometry, all 205 GPKGs
- `table_vs_attr_20261024.csv` — table vs attribute vs geometry, 203 rows
- `batch_area_audit.py`, `table_vs_attr.py` — scripts

## GPKG attribute fixes needed (attribute -> table canon)
- Kaftia: ~50 countries inflated +2% to +19% (same failure mode as Alwana, fixed
  2026-10-24 to 471,163.81). All table values match geometry; only attributes stale.
- Illypnia: Herasalem attr 136,420 (true 2,877, +4641%); Andalusia 5,691,113
  (true 1,073,415, +430%); Lagash 348,265 (true 175,894, +98%).
- Abyala: Balisca attr = 0.00 (true 4,704,984) — zeroed attribute.
- Abyala: Haramara attr 42,704 (geometry 41,293, +3.4%).
- Topology errors (geometry invalid, needs make_valid before measuring):
  Lurandia - Tecala, Lurandia - United Midlands.

## Wiki table-side outliers (table cell disagrees with geometry)
- Abyala - Haramara: table says 8,134,230; geometry is 41,293. Table cell wrong.
- Fosia - Pasundan: table 558,249 vs geometry 589,112 (-5.5%).
- Fosia - Pangkajene: table 365,316 vs geometry 370,237 (-1.3%).
- Abyala - Asikyira: table 674,225 vs geometry 693,172 (-2.7%).
- Abyala - Tapuya: table 1,358,830 vs geometry 1,375,332 (-1.2%).
- Abyala - Lacashe: table 221,514 vs geometry 222,827 (-0.6%).

## Open canon questions (not touched)
- Balboa: memory canon says 39,240 km2 (Panama-analogue) but both the Abyala table
  and the polygon measure ~296,000 km2. Needs a Carl ruling.
- Table countries with no GPKG: Buweran, Sanjara (Kaftia), Kalinovia (Illypnia),
  Bolodun and Kuvari Islands, Guajicutea, Kartak, Narubi, Tosaquia (Abyala).
