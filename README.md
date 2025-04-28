# FitFlux

**FitFlux** imports Fitbit data exported from [Google Takeout](https://takeout.google.com/settings/takeout) into an **InfluxDB** database, so you can visualize it beautifully in **Grafana**.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Grafana Dashboard](#grafana-dashboard)
- [Troubleshooting](#troubleshooting)

---

## Features

- Import Fitbit health and activity data into InfluxDB
- Visualize your personal fitness metrics with Grafana
- Simple setup using Google Takeout exports (using the Fitbit API to import historic data is quite impractical due to the rate-limitation thay have in place)

![localhost_3000_d_cek72djonbta8b_fitflux_orgId=1 from=2019-12-24T23_00_00 000Z to=2025-05-11T16_57_17 000Z timezone=browser](https://github.com/user-attachments/assets/04128853-baf9-4645-8f51-e6d1096c2158)

---

## Prerequisites

Before you begin, ensure you have:

- An instance of **InfluxDB version 1** running
- A **Grafana** server ready
- **Python 3.10+** installed
- `uv` (or your preferred Python environment manager) installed

---

## Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/smeukinou/FitFlux.git
   cd FitFlux
   ```

2. **Install dependencies** using `uv`:

   ```bash
   uv sync
   ```

3. **Set up InfluxDB**: Create a new database for the project:

   ```sql
   CREATE DATABASE FitFlux;
   ```

---

## Configuration

1. Create a `config.json` file in the project directory:

   ```json
   {
    "devicename": "Versa 2",
    "dbname": "FitFlux",
    "dbhost": "localhost",
    "dbport": 8086,
    "dbuser": "",
    "dbpassword": ""    
   }
   ```

2. Place your **Google Takeout** Fitbit data:

   - After downloading the Google Takeout export, **unzip** it inside a `Takeout/` directory **inside** the project folder.

---

## Usage

1. **Request your Fitbit data**:

   - Go to [Google Takeout](https://takeout.google.com/settings/takeout)
   - Select only **Fitbit** data and export it.

2. **Prepare the data**:

   - Unzip your Takeout archive into the `Takeout/` directory under the project root.

3. **Run the script**:

   ```bash
   uv run fitflux.py
   ```

4. **Wait** (intraday heartbeats data are quite long to process if you have multiple years of history):

   - The script will parse the Fitbit data and import it into your InfluxDB instance.

---

## Grafana Dashboard

- A ready-to-use Grafana dashboard template is available in the `grafana/` directory.
- To import:
  1. Open Grafana
  2. Go to **Dashboards** > **Import**
  3. Upload the dashboard JSON file
  4. Select your FitFlux InfluxDB data source when prompted

---

## Troubleshooting

- **No data appears in Grafana**:

  - Check that your InfluxDB connection parameters in `config.json` are correct.
  - Confirm the `Takeout/` directory is correctly placed and contains the extracted Fitbit files.

- **Script errors**:

  - Ensure your Python environment has all required dependencies installed.
  - Check that your InfluxDB instance is reachable.

## Credits
Heavily inspired from https://github.com/arpanghosh8453/fitbit-grafana, but he use of the **slow** FitBit API is a deal breaker to me.

