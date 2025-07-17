import requests
import yaml

GEONAMES_USERNAME = "anshuman07"  #replace with yourusername

def fetch_city_targets(min_population=500000, max_results=10):
    url = "http://api.geonames.org/searchJSON"
    params = {
        "q": "city",
        "maxRows": max_results,
        "orderby": "population",
        "featureClass": "P",  # populated places
        "style": "FULL",
        "username": GEONAMES_USERNAME
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    if "geonames" not in data:
        raise RuntimeError(f"GeoNames error: {data}")

    targets = []
    for place in data["geonames"]:
        pop = int(place.get("population", 0))
        if pop < min_population:
            continue

        targets.append({
            "name": place["name"].replace(" ", "_"),
            "lat": float(place["lat"]),
            "lon": float(place["lng"]),
            "priority": 1,
            "revisit_hours": 12
        })

    return targets

def save_to_yaml(targets, filename="targets.yaml"):
    with open(filename, "w") as f:
        yaml.dump(targets, f, default_flow_style=False)
    print(f"Saved {len(targets)} targets to {filename}")

if __name__ == "__main__":
    targets = fetch_city_targets(min_population=500000, max_results=25)
    save_to_yaml(targets)
