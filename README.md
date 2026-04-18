# Species Dashboard

A Streamlit dashboard for visualizing and reporting on species biodiversity data, connected to a PostgreSQL database.

## Database Configuration

> This project connects to a private PostgreSQL database and cannot be
> run locally without access credentials. It is shared here for
> portfolio and code reference purposes only.

## Project Structure

```
.
├── main.py                          # Main Streamlit app entry point
├── generate_report.py               # Single-species Word report generator
├── generate_report_2.py             # Filtered species Word report generator
├── report_format.py                 # Tab 3 detail view renderer
├── General_inf_template.docx        # Word template for single-species report
├── Filter_species_template_ver2.docx # Word template for filtered species report
└── .streamlit/
    └── secrets.toml                 # Database credentials (not committed)
```

## Features

- **Tab 1 – Overview of all species with interactive map, pie chart, and bar charts.
- **Tab 2 – Filter species by taxonomy, conservation status, and other criteria. Export filtered results as a Word report.
- **Tab 3 – Detailed view of a selected species including classification, conservation status, images, collection map, and export to Word report.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Configuration

Create a `.streamlit/secrets.toml` file with your PostgreSQL credentials:

```toml
[postgres]
host = "your_host"
port = 5432
dbname = "your_dbname"
user = "your_user"
password = "your_password"
```

## Running the App

```bash
streamlit run main.py
```

## Word Report Templates

Two `.docx` template files are required in the project root:

- `General_inf_template.docx` — used by `generate_report()` for single-species reports. Expected template variables: `spc`, `general_location`, `locations`, `quantity_through_years`, `image0`–`image3`.
- `Filter_species_template_ver2.docx` — used by `generate_report_2()` for filtered species reports. Expected template variables: `species`, `General_location`, `Locations_species`, `Quantity_through_years`, `Species_pie_chart`.

## Module Overview

| File | Description |
|---|---|
| `main.py` | App entry point. Handles DB queries, session state, data cleaning, and all three tabs. |
| `generate_report.py` | Generates a detailed `.docx` report for a single species including maps, bar chart, and species images. |
| `generate_report_2.py` | Generates a `.docx` report for a filtered set of species including maps, bar chart, and pie chart. |
| `report_format.py` | Renders the Tab 3 species detail UI: taxonomy info, conservation status, images, collection map, and report export button. |
