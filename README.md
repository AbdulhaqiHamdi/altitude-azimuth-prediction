# IoT-Based Temperature and Humidity Data Acquisition System for Solar Tracking Optimization Using Artificial Intelligence

An IoT-based environmental monitoring system that collects temperature and humidity data and uses Artificial Intelligence (AI) models to predict the Sun's altitude and azimuth angles base on environmental data. This project combines **IoT data acquisition, cloud data storage, machine learning, and web-based visualization** into an integrated system.

The project was originally developed as part of my undergraduate thesis in Physics at Universitas Indonesia.

---

## 🌐 Project Overview

Solar panels can produce different amounts of energy depending on their orientation relative to the Sun. Solar tracking systems are commonly used to adjust the panel's position throughout the day.

This project explores how **environmental data collected through an IoT system** can be combined with machine learning to estimate the Sun's apparent position.

The system collects:

- 🌡️ Temperature
- 💧 Humidity
- 🕒 Timestamp

The collected data are processed and used by machine learning models to predict:

- ☀️ Solar altitude
- 🧭 Solar azimuth

The results can then be visualized through a web-based dashboard.

The project is primarily intended as a demonstration of how **physical sensing, IoT systems, data processing, and machine learning** can be combined into a single application.

---

## 🔄 How the System Works

The overall workflow can be summarized as:

```text
Environmental Sensors (DHT11)
        │
        ▼
      ESP32
        │
        ▼
  Data Transmission
        │
        ▼
 Cloud / Data Storage
        │
        ▼
 Data Processing
        │
        ▼
 AI Prediction Models
   ┌────┴────┐
   ▼         ▼
  LSTM   Random Forest
   │         │
   └────┬────┘
        ▼
Solar Altitude & Azimuth
        │
        ▼
   Web Dashboard
```
## 📁 Repository Structure

### `make_a_model.ipynb`
- Jupyter Notebook used for developing, training, and evaluating AI models
- Includes data preprocessing, feature engineering, and performance analysis
- Serves as the primary experimentation environment for solar angle prediction

### `backend/`
- Contains Python scripts for model inference and prediction services
- Handles data input, preprocessing during inference, and output generation
- Designed to support integration with the web dashboard

### `data/`
- Contains datasets used throughout the research
- Includes raw sensor data, processed datasets, and CSV files for dashboard replay
- Supports reproducible experiments and offline visualization

### `firmware/`
- Contains firmware source code for the ESP32 microcontroller
- Responsible for temperature and humidity data acquisition
- Handles data transmission from ESP32 to the cloud database

### `frontend/`
- Contains source code for the web-based dashboard
- Implemented using HTML, JavaScript, and CSS
- Supports real-time visualization and CSV-based simulated streaming

---

## 📊 Dataset Description

Two main data sources are used in this research:

1. **IoT Sensor Data**
   - Temperature (°C)
   - Humidity (%)
   - Timestamp (UTC+7)

2. **Historical Weather Data**
   - Obtained from the **Open-Meteo Historical Weather API**
   - Used as an alternative data source for model evaluation and comparison

Only sample datasets are included in this repository for demonstration purposes.

---

## ⚙️ Technologies Used

### Hardware
- ESP32 Microcontroller  
- Temperature and Humidity Sensor  

### Software
- Python (data processing and AI modeling)
- TensorFlow / Keras (LSTM implementation)
- Scikit-learn (Random Forest)
- JavaScript, HTML, CSS (Web dashboard)
- Firebase Realtime Database

---

## 🚀 System Usage (Overview)

1. Deploy the firmware to the ESP32 to start environmental data acquisition.
2. Configure database credentials for cloud storage.
3. Run the AI prediction service for model inference.
4. Open the web dashboard to visualize sensor data and prediction results.

Detailed technical instructions are provided in the respective subdirectories.

---

## ⚠️ Limitations

- The AI models learn empirical correlations from environmental data rather than relying on deterministic astronomical equations.
- Reconstruction of solar altitude and azimuth is less accurate than physics-based Solar Position Algorithm (SPA) calculations.
- LSTM models require an initial data sequence before stable predictions can be produced.
- Model performance depends on data quality, sampling interval, and environmental variability.

---

## 📚 Academic Note

This repository is intended for educational and research purposes.  
The work emphasizes **system integration and instrumentation physics** combined with **data-driven modeling**, rather than replacing established astronomical methods.

---

## 👤 Author

**Abdulhaqi Hamdi**  
