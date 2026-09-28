# Contributing to human-override

Every data center you add makes the world's AI infrastructure more transparent.

## How to contribute

### 1. Add a data center

**Easiest:** [Open an issue](../../issues/new?template=add-datacenter.yml) with the details you know. We'll format and merge it.

**Best:** Submit a PR adding a row to `data/datacenters.csv` with as many fields as you can fill.

### 2. Enrich an existing record

Find a record missing power capacity, cooling type, or AI workload data? Add it with a source link.

### 3. Verify a record

Confirm that a facility still exists and is operational. Update `last_verified` to today's date.

## Data rules

1. **Every claim needs a source.** Add a URL to the `sources` column — news articles, permits, planning documents, satellite imagery, or operator websites.
2. **Only public information.** Never include classified, leaked, or non-public data.
3. **No speculation.** If you suspect a facility runs AI workloads but can't verify it, set `ai_workload_confidence` to `suspected`.
4. **Use the schema.** Run `python scripts/validate.py` before submitting a PR.

## ID format

Each record needs a unique `id` in the format: `{country_code}-{slugified-name}`

Examples:
- `us-equinix-sv5`
- `ie-microsoft-dublin-3`
- `sg-google-jurong-west`

## CSV format

Use the column order defined in `data/schema.json`. Use empty strings for unknown values, not "N/A" or "unknown" (except for enum fields like `status` and `ai_workload` where `unknown` is a valid value).

For array fields (`known_ai_tenants`, `fiber_providers`, `ix_connections`, `sources`), use semicolons as delimiters:

```
"OpenAI;Anthropic","Zayo;CenturyLink","https://source1.com;https://source2.com"
```

## Priority regions

We have good coverage in North America and Europe. We urgently need data from:

- 🌍 Africa (all countries)
- 🌏 South and Southeast Asia
- 🌎 South America
- 🌏 Central Asia
- 🌍 Middle East

## Running validation

```bash
pip install jsonschema
python scripts/validate.py
```

## Code of conduct

This project exists for transparency and public accountability. Contributions that target individuals, include non-public personal information, or promote violence will be rejected and the contributor banned.

## Questions?

Open a [discussion](../../discussions) or file an issue.
