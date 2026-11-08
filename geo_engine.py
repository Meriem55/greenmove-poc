"""
Module Geo : détection d'entrée dans une Zone à Faibles Émissions.
Algorithmes : Bounding Box (préfiltre) + Ray Casting (Point in Polygon).
Les coordonnées sont exprimées en latitude/longitude (WGS84).
"""
import json
from pathlib import Path

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def bounding_box(point, polygon):
    """Renvoie False immédiatement si le point est hors du rectangle englobant."""
    lats = [p["lat"] for p in polygon]
    lons = [p["lon"] for p in polygon]
    return (min(lats) <= point["lat"] <= max(lats)
            and min(lons) <= point["lon"] <= max(lons))

def point_on_segment(point, a, b, eps=1e-10):
    """Traite explicitement les points situés sur le bord d'un segment."""
    x, y = point["lon"], point["lat"]
    x1, y1 = a["lon"], a["lat"]
    x2, y2 = b["lon"], b["lat"]
    cross = (x-x1)*(y2-y1) - (y-y1)*(x2-x1)
    if abs(cross) > eps:
        return False
    return (min(x1, x2)-eps <= x <= max(x1, x2)+eps
            and min(y1, y2)-eps <= y <= max(y1, y2)+eps)

def point_in_polygon(point, polygon):
    """
    Ray Casting : lance un rayon horizontal depuis le point.
    Un nombre impair d'intersections signifie que le point est dedans.
    Les points sur le bord sont considérés comme dans la zone (choix prudent).
    """
    if len(polygon) < 3:
        raise ValueError("Le polygone doit contenir au moins 3 sommets.")
    if not bounding_box(point, polygon):
        return False

    inside = False
    n = len(polygon)
    for i in range(n):
        a = polygon[i]
        b = polygon[(i + 1) % n]
        if point_on_segment(point, a, b):
            return True
        yi, yj = a["lat"], b["lat"]
        xi, xj = a["lon"], b["lon"]
        intersects = ((yi > point["lat"]) != (yj > point["lat"]))
        if intersects:
            x_intersection = (xj - xi) * (point["lat"] - yi) / (yj - yi) + xi
            if point["lon"] < x_intersection:
                inside = not inside
    return inside

def run(polygon_path, gps_path):
    polygon = load_json(polygon_path)
    gps_points = load_json(gps_path)
    previous_inside = False
    results = []
    for p in gps_points:
        inside = point_in_polygon(p, polygon)
        if inside and not previous_inside:
            print(f'[ALERT ZFE] Entrée détectée - point GPS #{p.get("id")} à {p.get("timestamp")}')
        status = "IN" if inside else "OUT"
        results.append({"id": p.get("id"), "timestamp": p.get("timestamp"),
                        "lat": p["lat"], "lon": p["lon"], "status": status})
        previous_inside = inside
    return results

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    run(root / "data" / "lyon_polygon.json", root / "data" / "truck_gps.json")
