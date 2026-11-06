# Substation Maintenance Dashboard (2022)

An Excel Power Query and Power BI project using fictional substation data.

## Data
- Synthetic maintenance logs (618 rows, 600 after removing duplicates) and PD records (250 rows)
- Generated with a seeded Python script (`generate_substation_data.py`), so results are reproducible
- Five fictional sites, 11kV and 33kV. PD ranges are illustrative, informed by published PD research.

## Power Query steps
1. Promoted headers and set data types
2. Standardised site names (case, prefix removal)
3. Removed duplicate Log_IDs
4. Converted mixed-format dates using English (UK) locale
5. Added Resolution_Hours (rounded to 2 decimals)

## Dashboard
- Faults by site
- Average resolution time by site
- Monthly fault trend
- Status slicer (open/closed)
- KPI cards: total faults, open faults, average resolution

## Key figures
- Total faults: 600
- Open faults: 25
- Average resolution: 6.49 hours
- Highest fault count: Lembah Biru (140)
- Longest average resolution: Taman Mawar and Bukit Hijau (7.2 hours each)

## Files
- `substation_dashboard.xlsx`: Power Query workbook
- `substation_dashboard.pbix`: Power BI report
- `data/raw/`: generated CSVs
- `screenshots/dashboard.png`