# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flight data dashboard for Aeroporto Pinto Martins (SBFZ) in Fortaleza, Brazil. The dashboard analyzes ANAC (Brazilian Civil Aviation Agency) flight data with interactive visualizations.

## Development Commands

### Running the Dashboard
```bash
streamlit run dashboard.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Virtual Environment
The project uses a Python virtual environment in `.venv/`. Activate it before running commands:
```bash
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

## Architecture

### Single-File Application
The entire dashboard is contained in `dashboard.py`. It uses Streamlit's reactive model - the script reruns top-to-bottom on every user interaction.

### Data Flow
1. **Data Source**: JSON files from `/Users/tiago/anac_data_2025/` (hardcoded path)
2. **Loading**: `load_data()` uses `@st.cache_data` decorator to cache the loaded DataFrame across reruns
3. **Filtering**: Sidebar filters (airport, date range, airline) progressively filter the data
4. **Visualization**: Plotly charts display filtered data

### Key Components
- **Constants**: `DATA_PATH` and `TARGET_AIRPORT` at the top of the file control data source and default airport
- **Date Handling**: Four date columns (`PartidaPrevista`, `PartidaReal`, `ChegadaPrevista`, `ChegadaReal`) are converted to datetime with `errors='coerce'`
- **Encoding**: JSON files use `utf-8-sig` encoding to handle BOM (Byte Order Mark)

### Data Schema (ANAC format)
- `ICAOAeródromoOrigem` / `ICAOAeródromoDestino`: ICAO airport codes
- `ICAOEmpresaAérea`: Airline ICAO code
- `PartidaPrevista` / `PartidaReal`: Scheduled/actual departure times
- `ChegadaPrevista` / `ChegadaReal`: Scheduled/actual arrival times
- `SituaçãoVoo`: Flight status (e.g., "REALIZADO", "CANCELADO")
