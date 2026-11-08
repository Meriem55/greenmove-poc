from pathlib import Path
from geo_engine import run as run_geo
from safety_engine import analyze_csv

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    print("\\n=== MODULE 1 : ZFE ===")
    run_geo(ROOT / "data" / "lyon_polygon.json",
            ROOT / "data" / "truck_gps.json")
    print("\\n=== MODULE 2 : SAFETY ===")
    analyze_csv(ROOT / "data" / "accelerometer_data.csv",
                ROOT / "output" / "daily_score.json")
    print("\\nPOC terminé.")
