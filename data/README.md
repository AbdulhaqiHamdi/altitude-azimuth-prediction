# Data Directory

This directory contains datasets used for development, testing, evaluation, and visualization of an IoT-based environmental monitoring system with solar position prediction using machine learning models.

The datasets are organized to support:
- Model training and evaluation (LSTM and Random Forest)
- Web-based dashboard visualization (CSV replay mode)
- Reproducible experiments for academic purposes

---

## 🌐 Data Sources

### 1. IoT Sensor Data
- Source: Custom-built IoT data acquisition system
- Hardware: ESP32 microcontroller with environmental sensors
- Sensor: DHT11 (Temperature & Humidity)
- Location: Local experimental setup
- Sampling interval: Periodic (configurable)

This data represents direct environmental measurements and is used as ground truth for system validation.

---

### 2. Weather Data
- Source: **Open-Meteo Historical Weather API**
- Website: https://open-meteo.com/

Open-Meteo provides historical weather data aggregated from numerical weather prediction models, weather stations, satellite observations, and radar data.  
The API offers high temporal resolution (hourly) data and enables coverage of regions without direct weather station availability.

---

## 📁 File Description

### `dummy_data.csv`
- Dataset used for **dashboard replay mode**
- Contains environmental variables and corresponding model predictions
- Simulates real-time data streaming for visualization and demonstration purposes
- Data origin: Open-Meteo Historical Weather API (processed)

---

### `iot_sensor_data.csv`
- Raw data acquired from the IoT system
- Contains:
  - Temperature (°C)
  - Relative Humidity (%)
- Sensor: DHT11
- Used for validating system behavior against real sensor measurements

---

### `hourly_data.csv`
- Hourly historical weather data obtained from **Open-Meteo Historical Weather API**
- Used as an alternative data source and comparison scenario for model evaluation

---

### `final_data.csv`
- Processed dataset used for **machine learning model training and testing**
- Includes:
  - Environmental parameters
  - Time-based features
  - Target variables for solar altitude and azimuth prediction

This dataset is generated after data cleaning, preprocessing, and feature engineering.

---

### `make_data.py`
- Python script used for data preparation and dataset generation
- Performs data cleaning, preprocessing, and feature engineering
- Integrates raw IoT sensor data and weather data into a unified dataset
- Generates time-based features (e.g., hour/day encoding) required for machine learning models
- Outputs processed CSV files used for model training, testing, and dashboard visualization

This script represents the data processing pipeline prior to model development.

---

### `pull_request.csv`
- Dataset generated from Open-Meteo Historical Weather API requests
- Contains raw hourly weather data retrieved programmatically
- Serves as an intermediate data source before preprocessing
- Used to produce `hourly_data.csv` after data cleaning and formatting

This dataset represents the initial output of the data acquisition process prior to feature engineering and model preparation.

---

## 📌 Notes

- CSV files in this directory are intended for **offline analysis and visualization**.
- The web dashboard loads CSV files using the Fetch API; therefore, the project must be served via an HTTP server (local or remote).
- Some prediction columns may contain missing values (`NaN`) at the beginning of sequences due to windowing requirements in LSTM models.

---

## 🎓 Academic Context

All datasets in this directory are prepared to support:
- Transparent model evaluation
- Reproducible experimentation
- Visualization of system behavior in an academic setting

This data directory is part of an undergraduate thesis project in physics instrumentation and renewable energy systems.

---

## 📜 Disclaimer

The datasets provided here are intended for educational and research purposes only.  
External data sources remain subject to their respective licenses and terms of use.