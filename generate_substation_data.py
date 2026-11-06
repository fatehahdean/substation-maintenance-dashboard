"""
Generate synthetic substation maintenance logs and PD records for 2022.
Fictional sites. PD magnitude ranges are illustrative, informed by published PD research.
Run: python3 generate_substation_data.py
"""
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2022
N_LOGS = 600
N_PD = 250
OUT_DIR = Path("data/raw")

rng = np.random.default_rng(SEED)
START = datetime(2022, 1, 1)
SPAN_MIN = int((datetime(2022, 12, 31, 23, 59) - START).total_seconds() // 60)

# site code: (name, voltage, equipment types)
SITES = {
    "SS-01": ("Bukit Hijau", "33/11kV", ["Transformer", "Circuit Breaker", "Cable"]),
    "SS-02": ("Sungai Kelana", "33/11kV", ["Transformer", "Switchgear", "Cable"]),
    "SS-03": ("Taman Mawar", "11kV", ["Switchgear", "Cable", "RMU"]),
    "SS-04": ("Lembah Biru", "33/11kV", ["Transformer", "Circuit Breaker", "CT/VT"]),
    "SS-05": ("Jalan Seri", "11kV", ["RMU", "Switchgear", "Cable"]),
}

# fault type: (priority, median outage minutes, median repair hours)
FAULTS = {
    "Cable fault": ("High", 180, 8),
    "Cable joint failure": ("High", 240, 10),
    "Pole damage": ("Medium", 120, 6),
    "Voltage anomaly": ("Medium", 45, 3),
    "Transformer oil issue": ("High", 60, 12),
    "Switchgear alarm": ("Low", 30, 2),
    "Vegetation contact": ("Medium", 90, 4),
}
FAULT_WEIGHTS = np.array([0.22, 0.10, 0.12, 0.16, 0.10, 0.16, 0.14])

LOCATIONS = ["Winding", "Bushing", "Cable termination", "Cable joint",
             "Switchgear compartment", "Busbar"]

# Equipment register: one list of units per site
equipment = []
for code, (_, _, eq_types) in SITES.items():
    for eq in eq_types:
        prefix = eq.replace("/", "").replace(" ", "")[:3].upper()
        for i in range(1, int(rng.integers(3, 6)) + 1):
            equipment.append((code, eq, f"{code}-{prefix}-{i:02d}"))


def random_time():
    return START + timedelta(minutes=int(rng.integers(0, SPAN_MIN)))


def messy_date(dt):
    """Mostly ISO, but some rows use other formats, as real exports do."""
    r = rng.random()
    if r < 0.70:
        return dt.strftime("%Y-%m-%d %H:%M")
    if r < 0.85:
        return dt.strftime("%d/%m/%Y %H:%M")
    return dt.strftime("%d-%b-%Y %H:%M")


def make_logs():
    rows = []
    fault_names = list(FAULTS)
    for n in range(1, N_LOGS + 1):
        code, eq_type, eq_id = equipment[rng.integers(len(equipment))]
        fault = fault_names[rng.choice(len(fault_names), p=FAULT_WEIGHTS)]
        priority, med_outage, med_repair = FAULTS[fault]

        reported = random_time()
        is_open = rng.random() < 0.04
        if is_open:
            outage, resolved = None, None
        else:
            outage = int(round(rng.lognormal(np.log(med_outage), 0.5)))
            resolved = reported + timedelta(hours=float(rng.lognormal(np.log(med_repair), 0.4)))

        site_name = SITES[code][0]
        name_variant = str(rng.choice([site_name, site_name.upper(), "SS " + site_name.lower()],
                                      p=[0.80, 0.10, 0.10]))
        rows.append({
            "Log_ID": f"LOG-{n:04d}",
            "Site_Code": code,
            "Site_Name": name_variant,
            "Equipment_Type": eq_type,
            "Equipment_ID": eq_id,
            "Fault_Type": fault,
            "Date_Reported": messy_date(reported),
            "Date_Resolved": messy_date(resolved) if resolved else "",
            "Outage_Minutes": outage if outage is not None else "",
            "Priority": priority,
            "Status": "Open" if is_open else "Closed",
        })

    df = pd.DataFrame(rows)
    # Add ~3% duplicate rows, shuffled in, as a messy export would contain
    dupes = df.sample(frac=0.03, random_state=SEED)
    return pd.concat([df, dupes]).sample(frac=1, random_state=SEED).reset_index(drop=True)


def make_pd():
    rows = []
    for n in range(1, N_PD + 1):
        code, _, eq_id = equipment[rng.integers(len(equipment))]
        mag = float(rng.lognormal(np.log(60), 0.8))

        if mag < 50:
            band = "Low"
        elif mag < 150:
            band = "Medium"
        elif mag < 300:
            band = "High"
        else:
            band = "Critical"

        if rng.random() < 0.02:
            eq_id = f"{code}-XXX-99"  # orphan ID that matches no equipment

        rows.append({
            "PD_ID": f"PD-{n:04d}",
            "Site_Code": code,
            "Equipment_ID": eq_id,
            "Test_Date": messy_date(random_time()),
            "PD_Magnitude_pC": round(mag, 1),
            "Location_In_Asset": str(rng.choice(LOCATIONS)),
            "Severity_Band": band,
        })
    return pd.DataFrame(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    logs = make_logs()
    pd_df = make_pd()
    logs.to_csv(OUT_DIR / "maintenance_logs_2022.csv", index=False, encoding="utf-8")
    pd_df.to_csv(OUT_DIR / "pd_records_2022.csv", index=False, encoding="utf-8")
    print(f"Maintenance logs written: {len(logs)} rows (includes duplicates)")
    print(f"PD records written: {len(pd_df)} rows")


if __name__ == "__main__":
    main()