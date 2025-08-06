# datapopy

**datapopy** is a Python wrapper to work with [data.police.uk](https://data.police.uk) easily and reliably. It simplifies accessing UK police data via their public API, helping you fetch, filter, and analyze crime and policing information with minimal setup.

---

## 🚀 Features

- 🔍 Search crime data by location, date, or category
- 🗺️ Fetch street-level crime and outcomes
- 🧑‍✈️ Access police force information
- 🧩 Fetch neighbourhood boundary and team data
- ⚙️ Simple Pythonic interface around the raw API
- 🧪 Designed for analysts, data scientists, and developers

---

## 🧪 Prerequisites

- Python 3.8+
- `requests` library (installed automatically with pip)

Optional but recommended:

- `pandas` for data manipulation
- `matplotlib` or `plotly` for visualizations

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 📦 Installation

Clone and install locally:

```bash
git clone https://github.com/daa2618/datapopy.git
cd datapopy
pip install .
```

Or install directly using pip (once published on PyPI):

```bash
pip install datapopy
```

---

## 🎯 Usage

Here’s how to get started:

```python
from data_police_uk.datapopy import DataPoliceUK

client = DataPoliceUK()

# Get all UK police forces
forces = client.LIST_OF_FORCES

---
# Crimes Data
from data_police_uk.datapopy import CrimesData

crimes_data = CrimesData()
# Fetch street-level shoplifting crimes at a location
crimes = crimes_data.get_street_level_crimes_by_type(crime_id="shoplifting",
                                            lat=52.629729,
                                       lng=-1.131592,
                                       year="2025",
                                       month="01")
---
# Neighborhoods data
from data_police_uk.datapopy import Neighborhoods

neighborhood_data = Neighborhoods("metropolitan")
# Search neighbourhood info for a specific force
neighbourhoods = neighborhood_data.ALL_NEIGHBORHOOD_IDS_AND_NAMES
```

---

## 🧠 Example: Map street crimes in London

```python
import pandas as pd
import matplotlib.pyplot as plt

from data_police_uk.datapopy import CrimesData

crimes_data = CrimesData()
data = crimes_data.get_all_street_level_crimes(
                                            lat=52.629729,
                                       lng=-1.131592,
                                       year="2025",
                                       month="01")

df = pd.DataFrame(data)
df['category'].value_counts().plot(kind='bar', title="Crime Categories in London")
plt.show()
```

---

## 🧪 API Coverage

| Endpoint | Description |
|----------|-------------|
| `/forces` | List all police forces |
| `/forces/{id}` | Info about a force |
| `/crimes-street/all-crime` | Crime by lat/lng |
| `/outcomes-at-location` | Outcomes of crime |
| `/neighbourhoods` | Areas within force |
| `/neighbourhoods/{id}` | Specific area info |

See full API documentation: [https://data.police.uk/docs](https://data.police.uk/docs/)

---

## 🧾 Contributing

Contributions welcome! You can help by:

- Submitting bug reports or feature requests via Issues
- Improving documentation
- Writing tests or fixing bugs
- Extending API support (e.g., stop-and-search, priorities)

Please open a PR or reach out via GitHub Issues.

---

## ⚖️ License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 FAQ

**Q: Do I need an API key?**  
A: No, the [data.police.uk](https://data.police.uk) API is public and does not require authentication.

**Q: Is this an official wrapper?**  
A: No, this is an independent project built around their open API.

---

## 🔗 Related Projects

- [UK Police Data API Docs](https://data.police.uk/docs/)
- [data.police.uk GitHub](https://github.com/ukhomeoffice/police-api)
