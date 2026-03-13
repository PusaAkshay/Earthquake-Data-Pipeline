# Earthquake-Data-Pipeline

What is this project?

An end-to-end Data Engineering project on Azure that ingests earthquake data from the USGS API, processes it using a Medallion Architecture, and visualizes insights in a dashboard.

This project demonstrates how to build a modern data pipeline using cloud tools and big data processing.

Architecture
![Architecture](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/bbaaaa892760b5c2d84308fd371c300d130034ed/Architecture.png.png)

---

USGS REST API (all_day.geojson)
          ↓
Azure Data Factory (Daily Schedule Trigger)
  ├── Web Activity       → checks API is alive
  ├── Set Variable       → sets today_date (yyyy_MM_dd)
  └── Copy Activity      → saves raw JSON to ADLS
          ↓
ADLS Gen2 - Raw Container
(earthquake_yyyy_MM_dd.json)
          ↓
Databricks Job
  ├── Task 1: Autoloader Notebook
  │     raw JSON → Bronze Delta Table
  └── Task 2: DLT Pipeline
        Bronze → Silver → Gold
          ↓
Databricks Dashboard
(Today's Earthquake Analytics)
```

---

## 🥉🥈🥇 Medallion Architecture

| Layer | Location | Description |
|-------|----------|-------------|
| **Raw** | `abfss://raw@adlsearthquake.dfs.core.windows.net/earthquakes/` | Original JSON files from USGS API — never modified |
| **Bronze** | `abfss://bronze@adlsearthquake.dfs.core.windows.net/earthquake_data/` | Parsed Delta table via Autoloader — schema inferred |
| **Silver** | Unity Catalog → `silver` ADLS external location | Cleaned data — nulls dropped, DLT quality rules applied |
| **Gold** | Unity Catalog → `silver` ADLS external location | Enriched analytics-ready table — categories, flags, deduplication |

> **Note:** Unity Catalog was configured with the `silver` ADLS container as the external location. All DLT pipeline tables (bronze, silver, gold) are managed by Unity Catalog and stored in the silver container under the `earthquake.earthquake_db` schema.

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Azure Data Factory** | Pipeline orchestration, scheduling, API ingestion |
| **ADLS Gen2** | Data lake storage (raw, bronze, silver, gold containers) |
| **Azure Databricks** | Autoloader, Delta Live Tables, Jobs |
| **Delta Live Tables (DLT)** | Bronze → Silver → Gold transformation pipeline |
| **Unity Catalog** | Data governance, external locations, table management |
| **Databricks Dashboard** | Real-time earthquake analytics visualization |
| **GitHub** | Version control for ADF pipelines and Databricks notebooks |

---

## 📁 Repository Structure

```
Earthquake-Data-Pipeline/
├── ADF/
│   └── pipeline1.json          # ADF pipeline definition
├── Databricks/
│   ├── autoloader.py           # Autoloader: raw → bronze
│   └── dlt_pipeline.py         # DLT: bronze → silver → gold
└── README.md
```

---

## 🔄 Pipeline Flow

### 1. ADF Pipeline (Daily Trigger)
- **Web Activity** — GET request to USGS API to verify it's alive
- **Set Variable** — captures `today_date` as `yyyy_MM_dd`
- **Copy Activity** — downloads `all_day.geojson` and saves as `earthquake_yyyy_MM_dd.json` to raw container
- **Databricks Job Activity** — triggers Databricks Job

### 2. Autoloader (raw → bronze)

### 3. DLT Pipeline (bronze → silver → gold)

**Bronze Table** — parses nested JSON columns (`properties`, `geometry`), extracts all earthquake fields

**Silver Table** — applies DLT quality rules:

**Gold Table** — enriches data with business logic:


## 📈 Dashboard

Built using **Databricks Lakeview Dashboard** connected directly to `earthquake.earthquake_db.gold_earthquakes`.

Visuals include:
- 🗺️ **Point Map** — worldwide earthquake locations colored by magnitude category
- 🔢 **Total Earthquakes** — count of today's events
- 📊 **Avg & Max Magnitude** — key metrics
- 🌊 **Tsunami Alerts** — count of tsunami warnings
- 📉 **Earthquakes by Category** — bar chart (Major/Moderate/Minor/Micro)
- 📉 **Earthquakes by Depth** — bar chart (Shallow/Intermediate/Deep)
- 📋 **Top Earthquake Locations** — table sorted by magnitude

Dashboard query filters to today's data:
```sql
SELECT * FROM earthquake.earthquake_db.gold_earthquakes
WHERE DATE(event_time) = CURRENT_DATE()
```




## 📡 Data Source

**USGS Earthquake Hazards Program**
- Endpoint: `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`
- Updates: Every minute
- Coverage: All earthquakes worldwide in the last 24 hours
- License: Public domain (U.S. Government data)
