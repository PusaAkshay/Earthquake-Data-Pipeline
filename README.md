# Earthquake-Data-Pipeline

What is this project?

An end-to-end Data Engineering project on Azure that ingests earthquake data from the USGS API, processes it using a Medallion Architecture, and visualizes insights in a dashboard.

This project demonstrates how to build a modern data pipeline using cloud tools and big data processing.

Architecture
![Architecture](https://github.com/PusaAkshay/Earthquake-Data-Pipeline/blob/bbaaaa892760b5c2d84308fd371c300d130034ed/Architecture.png.png)

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
