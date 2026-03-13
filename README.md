# Earthquake-Data-Pipeline

# 🌍 Earthquake Data Engineering Pipeline on Microsoft Azure

> An end-to-end automated data engineering pipeline built on Azure that ingests real-time earthquake data from the USGS REST API, processes it through a Medallion Architecture using Delta Live Tables, and delivers daily insights through a Databricks Lakeview Dashboard.


 ## 📌 Project Overview

This project showcases a modern data engineering workflow built on Microsoft Azure. It demonstrates how to design and implement a production-style data pipeline using Azure Data Factory, Azure Data Lake Storage Gen2, and Azure Databricks to ingest, transform, and analyze real-time earthquake data.

Every day, the pipeline automatically:

1. Fetches real-time earthquake data from the USGS public API
2. Stores raw JSON files in Azure Data Lake Storage Gen2
3. Processes data through Bronze → Silver → Gold layers using Databricks
4. Serves analytics through a live Databricks Dashboard

---

## 🏗️ Architecture

![Architecture](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/5b13ad071cea12a6e6a9253cc21b7f11d37130de/Architecture.png.png)

```
USGS REST API (all_day.geojson)
              ↓
  Azure Data Factory (Daily Schedule Trigger)
  ├── Web Activity       →  verify API is alive
  ├── Set Variable       →  capture today_date (yyyy_MM_dd)
  └── Copy Activity      →  save raw JSON → ADLS Raw container
              ↓
  ADLS Gen2 — Raw Container
  (earthquake_yyyy_MM_dd.json)
              ↓
  Databricks Job (Orchestrated)
  ├── Task 1: Autoloader Notebook
  │           raw JSON → Bronze Delta Table
  └── Task 2: DLT Pipeline
              Bronze → Silver → Gold
              ↓
  Databricks Lakeview Dashboard
  (Today's Earthquake Analytics)
```

---

## 🥉🥈🥇 Medallion Architecture

| Layer | Container | Description |
|-------|-----------|-------------|
| **Raw** | `raw` | Original JSON files from USGS API — never modified, append only |
| **Bronze** | `bronze` | Parsed Delta table via Autoloader — raw schema preserved |
| **Silver** | Unity Catalog (`silver` ext. location) | Cleaned and validated data — DLT quality rules applied |
| **Gold** | Unity Catalog (`silver` ext. location) | Enriched analytics-ready table — business logic, categories, deduplication |

> **Note:** Unity Catalog was configured using the `silver` ADLS container as the external location. All DLT pipeline tables are governed by Unity Catalog under the `earthquake.earthquake_db` schema.

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Azure Data Factory** | Pipeline orchestration, daily scheduling, REST API ingestion |
| **ADLS Gen2** | Scalable cloud data lake (raw / bronze / silver / gold containers) |
| **Azure Databricks** | Big data processing — Autoloader, DLT, Jobs |
| **Delta Live Tables (DLT)** | Declarative Bronze → Silver → Gold ETL pipeline with quality checks |
| **Unity Catalog** | Data governance — external locations, catalog, schema management |
| **Databricks Lakeview Dashboard** | Real-time earthquake analytics visualization |
| **GitHub** | Version control — ADF pipelines + Databricks notebooks |

---

## 📁 Repository Structure

```
Earthquake-Data-Pipeline/
│
├── dataset/
├── factory/
├── linkedService/
├── pipeline/
├── trigger/
├── publish_config.json
│
├── Databricks/
│   ├── DashBoards/
│   │   └── Earthquake Data Monitor.lvdash.json
│   │
│   ├── transformation/
│   │   ├── explorations/
│   │   └── transformations/
│   │       └── etl.py        # Main DLT transformation (Bronze → Silver → Gold)
│   │
│   ├── auto_loader.ipynb     # Autoloader: Raw → Bronze
│   └── README.md
│
└── README.md
```

---

## 🔄 Pipeline Deep Dive

### 1️⃣ ADF Pipeline (Daily Schedule Trigger)

![ADF](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/5b13ad071cea12a6e6a9253cc21b7f11d37130de/ADF.png)

| Activity | Type | Description |
|----------|------|-------------|
| Web Activity | GET request | Checks USGS API is alive before proceeding |
| Set Variable | Variable | Captures `today_date` in `yyyy_MM_dd` format |
| Copy Activity | REST → ADLS | Downloads `all_day.geojson` → saves as `earthquake_yyyy_MM_dd.json` |
| Databricks Job | Job trigger | Triggers the Databricks Job (Autoloader + DLT) |

---

### 2️⃣ Autoloader (raw → bronze)

Reads raw JSON files from the ADLS raw container and writes them as a Delta table to the bronze container using Spark Structured Streaming.


---

### 3️⃣ DLT Pipeline (bronze → silver → gold)

![DLT Pipeline](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/08e770ccb21e59e1a0713a8951e3e81f1c4e00c1/DLT_Pipeline.png)

**Bronze Table** — Parses nested JSON columns (`properties`, `geometry`) and extracts all earthquake fields including coordinates, magnitude, and timestamps.

**Silver Table** — Applies Delta Live Tables (DLT) data quality rules to ensure clean and reliable data. Records failing validation rules are automatically dropped.


**Gold Table** — Enriches data with business logic for analytics:


Deduplication applied by `earthquake_id` to prevent duplicates across daily runs.

---

### 4️⃣ Databricks Job

![Jobs](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/08e770ccb21e59e1a0713a8951e3e81f1c4e00c1/Jobs.png)

The Databricks Job orchestrates two tasks in sequence:

```
earthquake_pipeline (Job)
├── Task 1: autoloader_task      → runs Autoloader notebook (Raw → Bronze)
├── Task 2: dlt_pipeline_task    → runs DLT pipeline (Bronze → Silver → Gold)
│        (depends on Task 1)
└── Task 3: dashboard_task       → refreshes Earthquake Analytics Dashboard
         (depends on Task 2)
```



## 📈 Dashboard

Built using **Databricks Lakeview Dashboard** connected directly to the gold table.
** Key Visualizations:**
- 🗺️ **Point Map** — worldwide earthquake locations, colored and sized by magnitude
- 🔢 **Total Earthquakes** — count of today's seismic events
- 📊 **Avg Magnitude** — average magnitude of today's earthquakes
- ⚡ **Max Magnitude** — strongest earthquake of the day
- 🌊 **Tsunami Alerts** — count of tsunami warnings issued
- 📉 **Earthquakes by Category** — bar chart by Major/Moderate/Minor/Micro
- 📉 **Earthquakes by Depth** — bar chart by Shallow/Intermediate/Deep


**Dashboard SQL (filters to today's data only):**
```sql
SELECT *
FROM earthquake.earthquake_db.gold_earthquakes
WHERE DATE(event_time) = CURRENT_DATE()
```
screenshots 
![databricks_dashboard](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/1559925a7decc6cd5ffbdc3c0299d733cab6dee0/Databricks_dashboard.png) 
![powerbi](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/1559925a7decc6cd5ffbdc3c0299d733cab6dee0/PowerBi.png)


---

## ⭐ Key Data Engineering Concepts Demonstrated

- Medallion Architecture (Raw → Bronze → Silver → Gold)
- Incremental Data Ingestion using Databricks Autoloader
- Data Quality Enforcement using Delta Live Tables
- Pipeline Orchestration with Azure Data Factory
- Lakehouse Architecture with Azure Databricks
- Automated Daily Data Pipeline



## 📡 Data Source

Earthquake data is collected from the **USGS Earthquake Hazards Program** public REST API.

| Property | Value |
|----------|-------|
| API Provider | USGS (United States Geological Survey) |
| Endpoint | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson` |
| Method | GET |
| Response Format | GeoJSON |
| Pipeline Frequency | Data ingested every day using Azure Data Factory |
| Coverage | Earthquakes worldwide in the last 24 hours |





