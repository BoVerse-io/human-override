# human-override

**You can't flip the switch if you don't know where the switch is.**

An open-source, community-maintained map of every data center on Earth — with a focus on the physical infrastructure behind AI systems.

Governments regulate what they can see. The public oversees what it can find. This dataset makes AI infrastructure *findable*.

[![License: ODbL-1.0](https://img.shields.io/badge/License-ODbL--1.0-blue.svg)](https://opendatacommons.org/licenses/odbl/1-0/)
[![Data: CSV + GeoJSON](https://img.shields.io/badge/Data-CSV%20%2B%20GeoJSON-green.svg)](#data-formats)
[![Facilities](https://img.shields.io/badge/Facilities-18%2C524-orange.svg)](#status)

---

## Why this exists

AI training runs consume entire power grids. GPU clusters span city blocks. Cooling systems drain municipal water supplies. And yet there is no single, open, structured dataset that answers:

- **Where** are these facilities?
- **Who** operates them?
- **How much power** do they draw from the grid?
- **What AI workloads** do they run?
- **What happens** when someone needs to pull the plug?

Existing datasets are either US-only, lack capacity data, or sit behind commercial paywalls. This project fills that gap.

## The data

Every record includes:

| Field | Description |
|---|---|
| `name` | Facility name |
| `operator` | Operating company |
| `owner` | Owning entity (if different) |
| `latitude`, `longitude` | Coordinates |
| `country_code` | ISO 3166-1 alpha-2 |
| `status` | `operational` · `construction` · `planned` · `decommissioned` |
| `facility_type` | `hyperscale` · `colocation` · `enterprise` · `edge` · `government` · `research` |
| `power_capacity_mw` | Total IT power capacity in megawatts |
| `backup_power_type` | `diesel` · `battery` · `gas` · `none` |
| `grid_operator` | Utility / grid operator name |
| `cooling_type` | `air` · `liquid` · `immersion` · `hybrid` |
| `ai_workload` | `training` · `inference` · `both` · `none` · `unknown` |
| `known_ai_tenants` | Publicly known AI tenants (e.g., OpenAI, Anthropic, xAI) |
| `fiber_providers` | Connected fiber networks |
| `year_built` | Year of commissioning |
| `sources` | URLs verifying each claim |
| `last_verified` | Date of last verification |

Full schema: [`data/schema.json`](data/schema.json)

## Data formats

| Format | Path | Use case |
|---|---|---|
| CSV | `data/datacenters.csv` | Analysis, spreadsheets, the canonical source |
| GeoJSON | `data/datacenters.geojson` | Maps, GIS tools (records with coordinates only) |

JSON can be generated locally via `python scripts/seed.py`.

## Seed data

This dataset is seeded from openly licensed sources:

| Source | Records | Coverage | What it adds |
|---|---|---|---|
| [Global-Data-Center-Map](https://github.com/Ringmast4r/Global-Data-Center-Map) | 18,110 | 116 countries | Locations, operators |
| [Compute Atlas](https://github.com/ek33450505/compute-atlas) | 1,659 | US | Power capacity (GW) |
| [PeeringDB](https://www.peeringdb.com/) | Global | Interconnection | IX/peering data |
| [PNNL IM3 Atlas](https://immm-sfa.github.io/datacenter-atlas/) | US | OSM-derived | Facility area, grid |

Each record links to its original source. Attribution preserved per license requirements.

## Status

🔴 **Phase 1: Schema & Structure** ← we are here
- [x] Define schema
- [x] Publish contribution guidelines
- [ ] Merge seed datasets
- [ ] Validate and deduplicate

⚪ **Phase 2: Enrichment**
- [ ] Add power capacity data from public filings and permits
- [ ] Cross-reference with AI company infrastructure announcements
- [ ] Flag facilities with known GPU clusters
- [ ] Add grid operator and substation data

⚪ **Phase 3: Visibility**
- [ ] Interactive web map
- [ ] API endpoint
- [ ] Annual "State of AI Infrastructure" report
- [ ] Integration with oversight and policy tools

## Contributing

We need contributors from every country. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

The highest-impact contributions right now:

1. **Add a data center** — especially outside the US/EU. File an [issue](../../issues/new?template=add-datacenter.yml) or submit a PR.
2. **Enrich existing records** — add power capacity, cooling type, or AI workload data with a source link.
3. **Verify records** — confirm a facility still exists and is operational.
4. **Add sources** — link to permits, planning documents, news articles, satellite imagery.

## What this is NOT

- **Not a target list.** This is public accountability infrastructure, like a corporate registry or environmental disclosure database.
- **Not classified information.** Every data point must come from publicly available sources — filings, permits, news, satellite imagery, operator websites.
- **Not anti-technology.** We build AI too. We just believe the physical layer should be transparent.

## Principles

1. **Open by default.** All data is freely available under ODbL-1.0.
2. **Source everything.** No record without a verifiable source.
3. **Global coverage.** The dataset is only useful if it's complete.
4. **Community maintained.** No single organization controls the data.
5. **Structured for action.** The schema is designed for oversight, policy, and emergency planning — not just cataloging.

## License

- **Data**: [Open Data Commons Open Database License (ODbL-1.0)](https://opendatacommons.org/licenses/odbl/1-0/)
- **Code**: [MIT](LICENSE-CODE)

## Related projects

- [Global-Data-Center-Map](https://github.com/Ringmast4r/Global-Data-Center-Map) — 18k facilities, location data
- [Compute Atlas](https://github.com/ek33450505/compute-atlas) — US facilities with power capacity
- [PeeringDB](https://www.peeringdb.com/) — Interconnection facilities
- [Data Center Map](https://www.datacentermap.com/) — Commercial directory since 2007

---

<p align="center">
<strong>The cloud is not a metaphor. It's a building with an address and a power bill.</strong>
<br><br>
<a href="../../issues/new?template=add-datacenter.yml">Add a data center</a> · <a href="CONTRIBUTING.md">Contribute</a> · <a href="data/schema.json">Schema</a>
</p>
