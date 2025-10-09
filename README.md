# datapopy

`datapopy` is a Python wrapper for the public [data.police.uk](https://data.police.uk) API. It smooths over the raw HTTP interface so you can explore UK policing data - forces, neighbourhoods, crimes, and stop-and-search reports - without rebuilding the basics every time.

## Features
- Retrieve the catalogue of UK police forces and fuzzy-search by name or ID.
- Query street-level crimes by category, coordinates, location IDs, or custom polygons.
- Pull outcomes, stop-and-search data, and other time-bound datasets with consistent helpers.
- Discover neighbourhood details including boundaries, priorities, police teams, and events.
- Generate GeoDataFrames for neighbourhood boundaries when `geopandas` is available.

## Requirements
- Python 3.8 or newer
- Core dependency: `requests` (installed automatically)
- Optional: `pandas`/`matplotlib` for analysis and plotting, `geopandas`/`shapely` for spatial workflows

## Installation

### From source
```bash
git clone https://github.com/daa2618/datapopy.git
cd datapopy
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -e .
```

### From PyPI
The project is preparing for an initial release. Once published you will be able to run:
```bash
pip install datapopy
```

## Quickstart
```python
from data_police_uk.datapopy import DataPoliceUK

client = DataPoliceUK()
forces = client.LIST_OF_FORCES

print(f"{len(forces)} police forces found")
print(forces[0])
```
`LIST_OF_FORCES` returns a list of dictionaries with `id`/`name` keys that can be passed to the specialist helpers below.

## Working with crime data
```python
from data_police_uk.datapopy import CrimesData

crimes = CrimesData()

# Fetch shoplifting incidents around Leicester in January 2024
shoplifting = crimes.get_street_level_crimes_by_type(
    crime_id="shoplifting",
    lat=52.629729,
    lng=-1.131592,
    year="2024",
    month="01",
)

# Fetch all available street-level crimes for the same point
all_crimes = crimes.get_all_street_level_crimes(
    lat=52.629729,
    lng=-1.131592,
    year="2024",
    month="01",
)

# Use a bounding box (poly) if you need a custom polygon
poly = [
    "52.636,-1.135",
    "52.636,-1.120",
    "52.622,-1.120",
    "52.622,-1.135",
]
crimes_in_area = crimes.get_all_street_level_crimes(bounding_box=poly)
```

`CrimesData` exposes additional helpers for outcomes, available datasets, and crime categories. Consult the inline docstrings for more options.

## Exploring neighbourhoods
```python
from data_police_uk.datapopy import Neighborhoods

met = Neighborhoods("metropolitan")

# List neighbourhoods served by the Metropolitan Police
neighbourhoods = met.ALL_NEIGHBORHOOD_IDS_AND_NAMES

# Fetch detailed information and priorities
kensington = met.get_specific_neighborhood_info("EA0201")
priority_items = met.get_neighborhood_priorities("EA0201")

# Convert all neighbourhood polygons to a GeoDataFrame (requires geopandas)
gdf = met.POLICE_FORCE_BOUNDARY
```

## Stop and search data
```python
from data_police_uk.datapopy import StopAndSearches

stop_search = StopAndSearches()
march_stops = stop_search.get_stop_searches_for_coords(
    lat=52.629729,
    lng=-1.131592,
    year="2024",
    month="03",
)
```

## Example: Visualise crime counts
```python
import pandas as pd
import matplotlib.pyplot as plt

from data_police_uk.datapopy import CrimesData

crimes = CrimesData()
data = crimes.get_all_street_level_crimes(
    lat=51.5074,
    lng=-0.1278,
    year="2024",
    month="01",
)

df = pd.DataFrame(data)
df["category"].value_counts().sort_values().plot.barh(title="London crimes (Jan 2024)")
plt.tight_layout()
plt.show()
```
This example assumes `pandas` and `matplotlib` are installed in your environment.

## API coverage

| Endpoint | Purpose |
| --- | --- |
| `/forces` | List all police forces |
| `/forces/{id}` | Retrieve information about a single force |
| `/crimes-street/{crime-id}` | Retrieve crimes by category, coordinates, or polygon |
| `/outcomes-at-location` | Retrieve street-level outcomes |
| `/stops-street` | Retrieve stop-and-search reports |
| `/{force}/neighbourhoods` | List neighbourhoods served by a force |
| `/{force}/neighbourhoods/{id}` | Retrieve details, priorities, personnel, and boundary geometry |

Refer to the official docs for the full API surface: <https://data.police.uk/docs/>

## Development
- Install dependencies with `pip install -e .[dev]` when development extras are published, or manually add the tools from `pyproject.toml`.
- Run the test suite (when available) with `pytest`.
- Use a virtual environment to avoid polluting your global Python installation.

## Contributing
Contributions are very welcome. Helpful ways to get involved:
- Report bugs or feature requests through GitHub Issues.
- Improve documentation and examples.
- Add or expand tests to cover new API endpoints.
- Extend coverage to additional datasets (e.g. priorities, senior staff, stop-and-search outcomes).

Please open a pull request once your change is ready.

## FAQ
**Do I need an API key?**  
No. The [data.police.uk](https://data.police.uk) API is open and does not require authentication.

**Is this an official wrapper?**  
Not currently. `datapopy` is a community project that builds on top of the public API.

## License
This project is distributed under the [MIT License](LICENSE).
