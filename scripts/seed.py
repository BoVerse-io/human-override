#!/usr/bin/env python3
"""
Seed the human-override dataset from open sources.

Downloads and merges:
1. Global-Data-Center-Map (18k+ facilities, 116 countries)
2. Compute Atlas (1.6k US facilities with power capacity)

Usage:
    pip install requests
    python scripts/seed.py
"""

import csv
import json
import re
import sys
from io import StringIO
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_CSV = REPO_ROOT / "data" / "datacenters.csv"
OUTPUT_JSON = REPO_ROOT / "data" / "datacenters.json"
OUTPUT_GEOJSON = REPO_ROOT / "data" / "datacenters.geojson"

GDCM_CSV_URL = "https://raw.githubusercontent.com/Ringmast4r/Global-Data-Center-Map/main/datacenters.csv"
COMPUTE_ATLAS_JSON_URL = "https://raw.githubusercontent.com/ek33450505/compute-atlas/main/data/facilities.json"

COUNTRY_TO_CODE = {}  # populated at runtime from GDCM data

COLUMNS = [
    "id", "name", "operator", "owner", "address", "city", "state_province",
    "country", "country_code", "latitude", "longitude", "status",
    "facility_type", "year_built", "year_decommissioned",
    "power_capacity_mw", "backup_power_type", "backup_power_duration_hours",
    "grid_operator", "grid_substation",
    "on_site_generation_type", "on_site_generation_mw",
    "cooling_type", "water_usage_m3_per_day", "pue", "total_area_sqm",
    "ai_workload", "ai_workload_confidence", "known_ai_tenants",
    "gpu_cluster_known", "fiber_providers", "ix_connections",
    "submarine_cable_landing", "jurisdiction", "government_facility",
    "sources", "last_verified", "seed_source", "notes",
]


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


def make_id(country_code, name, seen_ids):
    base = f"{country_code.lower()}-{slugify(name)}"
    if not base or base == country_code.lower() + "-":
        base = f"{country_code.lower()}-unnamed"
    candidate = base
    counter = 2
    while candidate in seen_ids:
        candidate = f"{base}-{counter}"
        counter += 1
    seen_ids.add(candidate)
    return candidate


def fetch_gdcm():
    """GDCM CSV columns: name, company, city, state, country, address (no lat/lon)."""
    print("Fetching Global-Data-Center-Map...")
    resp = requests.get(GDCM_CSV_URL, timeout=120)
    resp.raise_for_status()
    reader = csv.DictReader(StringIO(resp.text))
    records = []
    seen_ids = set()

    for row in reader:
        name = (row.get("name") or "").strip()
        if not name:
            continue

        country = (row.get("country") or "").strip()
        cc = "XX"

        record = {col: "" for col in COLUMNS}
        record["id"] = make_id(cc, name, seen_ids)
        record["name"] = name
        record["operator"] = (row.get("company") or "").strip()
        record["address"] = (row.get("address") or "").strip()
        record["city"] = (row.get("city") or "").strip()
        record["state_province"] = (row.get("state") or "").strip()
        record["country"] = country
        record["country_code"] = cc
        record["status"] = "operational"
        record["facility_type"] = "unknown"
        record["ai_workload"] = "unknown"
        record["ai_workload_confidence"] = "none"
        record["gpu_cluster_known"] = "false"
        record["submarine_cable_landing"] = "false"
        record["government_facility"] = "false"
        record["sources"] = "https://data-center-map.com/"
        record["seed_source"] = "global-data-center-map"
        records.append(record)

    print(f"  -> {len(records)} records from GDCM")
    return records


def fetch_compute_atlas():
    """Compute Atlas is JSON with nested location/capacityMw objects."""
    print("Fetching Compute Atlas...")
    resp = requests.get(COMPUTE_ATLAS_JSON_URL, timeout=120)
    resp.raise_for_status()
    facilities = resp.json()
    records = []
    seen_ids = set()

    for fac in facilities:
        name = (fac.get("name") or "").strip()
        if not name:
            continue

        loc = fac.get("location") or {}
        lat = loc.get("lat", "")
        lon = loc.get("lon", "")
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            lat, lon = "", ""

        cap = fac.get("capacityMw") or {}
        power = cap.get("operational") or cap.get("total") or ""
        if power:
            try:
                power = str(float(power))
            except (ValueError, TypeError):
                power = ""

        status = fac.get("status", "operational")
        if status not in ("operational", "construction", "planned", "decommissioned"):
            status = "operational"

        source_urls = []
        for s in (fac.get("sources") or []):
            url = s.get("url", "") if isinstance(s, dict) else str(s)
            if url:
                source_urls.append(url)
        if not source_urls:
            source_urls = ["https://www.compute-atlas.com/data"]

        record = {col: "" for col in COLUMNS}
        record["id"] = make_id("us", name, seen_ids)
        record["name"] = name
        record["operator"] = (fac.get("operator") or "").strip()
        record["address"] = (loc.get("street") or "").strip()
        record["city"] = (loc.get("city") or "").strip()
        record["state_province"] = (loc.get("state") or "").strip()
        record["country"] = "United States"
        record["country_code"] = "US"
        record["latitude"] = lat
        record["longitude"] = lon
        record["status"] = status
        record["facility_type"] = "unknown"
        record["power_capacity_mw"] = power
        record["ai_workload"] = "unknown"
        record["ai_workload_confidence"] = "none"
        record["gpu_cluster_known"] = "false"
        record["submarine_cable_landing"] = "false"
        record["government_facility"] = "false"
        record["sources"] = ";".join(source_urls)
        record["seed_source"] = "compute-atlas"
        records.append(record)

    print(f"  -> {len(records)} records from Compute Atlas")
    return records


def deduplicate(records):
    """Basic deduplication by name + country proximity."""
    seen = {}
    deduped = []
    for r in records:
        key = (r["name"].lower().strip(), r["country_code"])
        if key in seen:
            existing = seen[key]
            for col in COLUMNS:
                if not existing[col] and r[col]:
                    existing[col] = r[col]
        else:
            seen[key] = r
            deduped.append(r)
    return deduped


def write_csv(records):
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} records to {OUTPUT_CSV}")


def write_json(records):
    cleaned = []
    for r in records:
        rec = {}
        for k, v in r.items():
            if v == "":
                rec[k] = None
            elif k in ("latitude", "longitude", "power_capacity_mw",
                        "backup_power_duration_hours", "on_site_generation_mw",
                        "water_usage_m3_per_day", "pue", "total_area_sqm"):
                try:
                    rec[k] = float(v)
                except (ValueError, TypeError):
                    rec[k] = None
            elif k in ("year_built", "year_decommissioned"):
                try:
                    rec[k] = int(v)
                except (ValueError, TypeError):
                    rec[k] = None
            elif k in ("gpu_cluster_known", "submarine_cable_landing", "government_facility"):
                rec[k] = v.lower() == "true"
            elif k in ("known_ai_tenants", "fiber_providers", "ix_connections", "sources"):
                rec[k] = [s.strip() for s in v.split(";") if s.strip()] if v else []
            else:
                rec[k] = v
        cleaned.append(rec)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(cleaned)} records to {OUTPUT_JSON}")
    return cleaned


def write_geojson(records_json):
    features = []
    for r in records_json:
        if r.get("latitude") is not None and r.get("longitude") is not None:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [r["longitude"], r["latitude"]],
                },
                "properties": {k: v for k, v in r.items() if k not in ("latitude", "longitude")},
            }
            features.append(feature)

    geojson = {"type": "FeatureCollection", "features": features}
    with open(OUTPUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)
    print(f"Wrote {len(features)} features to {OUTPUT_GEOJSON}")


def main():
    print("=== human-override seed script ===\n")
    gdcm = fetch_gdcm()
    compute = fetch_compute_atlas()

    all_records = gdcm + compute
    print(f"\nTotal before dedup: {len(all_records)}")

    records = deduplicate(all_records)
    print(f"Total after dedup:  {len(records)}")

    records.sort(key=lambda r: (r["country_code"], r["name"]))

    write_csv(records)
    cleaned = write_json(records)
    write_geojson(cleaned)

    print("\nDone. Run 'python scripts/validate.py' to check the data.")


if __name__ == "__main__":
    main()
