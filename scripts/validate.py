#!/usr/bin/env python3
"""Validate datacenters.csv against schema.json."""

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "data" / "schema.json"
CSV_PATH = REPO_ROOT / "data" / "datacenters.csv"

ARRAY_FIELDS = {"known_ai_tenants", "fiber_providers", "ix_connections", "sources"}
BOOLEAN_FIELDS = {"gpu_cluster_known", "submarine_cable_landing", "government_facility"}
NUMBER_FIELDS = {
    "latitude", "longitude", "power_capacity_mw", "backup_power_duration_hours",
    "on_site_generation_mw", "water_usage_m3_per_day", "pue", "total_area_sqm",
}
INTEGER_FIELDS = {"year_built", "year_decommissioned"}


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def parse_row(row, schema):
    errors = []
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for field in required:
        if field not in row or row[field].strip() == "":
            errors.append(f"missing required field: {field}")

    for field, value in row.items():
        if field not in props:
            continue
        if value.strip() == "":
            continue

        prop = props[field]
        allowed_types = prop.get("type", "string")
        if isinstance(allowed_types, str):
            allowed_types = [allowed_types]

        if field in ARRAY_FIELDS:
            pass
        elif field in BOOLEAN_FIELDS:
            if value.lower() not in ("true", "false"):
                errors.append(f"{field}: expected boolean, got '{value}'")
        elif field in NUMBER_FIELDS:
            try:
                float(value)
            except ValueError:
                errors.append(f"{field}: expected number, got '{value}'")
        elif field in INTEGER_FIELDS:
            try:
                int(value)
            except ValueError:
                errors.append(f"{field}: expected integer, got '{value}'")

        if "enum" in prop:
            enum_values = [v for v in prop["enum"] if v is not None]
            if value not in enum_values and value.strip() != "":
                errors.append(f"{field}: '{value}' not in {enum_values}")

        if "pattern" in prop:
            import re
            if not re.match(prop["pattern"], value):
                errors.append(f"{field}: '{value}' does not match pattern {prop['pattern']}")

        if "minimum" in prop and field in NUMBER_FIELDS:
            try:
                if float(value) < prop["minimum"]:
                    errors.append(f"{field}: {value} below minimum {prop['minimum']}")
            except ValueError:
                pass

        if "maximum" in prop and field in NUMBER_FIELDS:
            try:
                if float(value) > prop["maximum"]:
                    errors.append(f"{field}: {value} above maximum {prop['maximum']}")
            except ValueError:
                pass

    return errors


def main():
    if not CSV_PATH.exists():
        print(f"No data file found at {CSV_PATH}")
        print("Run the seed script first or add data manually.")
        sys.exit(0)

    schema = load_schema()
    error_count = 0
    row_count = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row_count += 1
            errors = parse_row(row, schema)
            if errors:
                error_count += len(errors)
                for err in errors:
                    print(f"Row {i} ({row.get('id', '???')}): {err}")

    if error_count == 0:
        print(f"Validated {row_count} records. All good.")
    else:
        print(f"\n{error_count} error(s) in {row_count} records.")
        sys.exit(1)


if __name__ == "__main__":
    main()
