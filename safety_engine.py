"""
Module Safety : détection pédagogique des freinages violents.
L'annexe de l'énoncé précise que l'axe Y est longitudinal et qu'un freinage
est une valeur acc_y inférieure à -2.5 m/s².
"""
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

THRESHOLD = -2.5  # m/s², selon l'annexe 3 de l'énoncé

def analyze_csv(csv_path, output_path):
    events = []
    total_rows = 0
    valid_rows = 0

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "acc_x", "acc_y", "acc_z"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Colonnes attendues : {sorted(required)}")

        for row_number, row in enumerate(reader, start=2):
            total_rows += 1
            try:
                timestamp = float(row["timestamp"])
                acc_x = float(row["acc_x"])
                acc_y = float(row["acc_y"])
                acc_z = float(row["acc_z"])
            except (TypeError, ValueError):
                print(f"[IGNORÉ] Ligne {row_number} : données non numériques.")
                continue

            valid_rows += 1
            # Filtrage logique : on examine l'axe longitudinal Y, on vérifie
            # que les trois mesures sont numériques, puis on applique le seuil.
            # On ne moyenne pas les échantillons : cela pourrait effacer le pic
            # bref -3.45 m/s² présent dans le jeu de données fourni.
            if acc_y < THRESHOLD:
                events.append({
                    "timestamp": timestamp,
                    "datetime_utc": datetime.fromtimestamp(
                        timestamp, tz=timezone.utc
                    ).isoformat(),
                    "event": "HARSH_BRAKING",
                    "axis": "Y",
                    "acc_y_m_s2": acc_y,
                    "threshold_m_s2": THRESHOLD,
                    "severity": "HIGH"
                })
                print(f"[ALERT SAFETY] Freinage violent à t={timestamp} : acc_y={acc_y} m/s²")

    result = {
        "date_generated_utc": datetime.now(timezone.utc).isoformat(),
        "threshold_m_s2": THRESHOLD,
        "rows_read": total_rows,
        "valid_rows": valid_rows,
        "harsh_braking_count": len(events),
        "events": events
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[OK] Résultat enregistré dans : {output_path}")
    return result

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    analyze_csv(root / "data" / "accelerometer_data.csv",
                root / "output" / "daily_score.json")
