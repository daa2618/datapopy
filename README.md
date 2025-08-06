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
from datapopy import PoliceClient

client = PoliceClient()

# Get all UK police forces
forces = client.get_forces()

# Fetch street-level crimes at a location
crimes = client.get_crimes_at_location(lat=51.5074, lng=-0.1278, date="2023-07")

# Search neighbourhood info for a specific force
neighbourhoods = client.get_neighbourhoods("metropolitan")
```

---

## 🧠 Example: Map street crimes in London

```python
import pandas as pd
import matplotlib.pyplot as plt

from datapopy import PoliceClient

client = PoliceClient()
data = client.get_crimes_at_location(lat=51.5074, lng=-0.1278, date="2023-06")

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
