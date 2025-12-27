# IoT-Based Temperature and Humidity Data Acquisition System for Solar Tracking Optimization Using Artificial Intelligence

This repository contains the implementation of an Internet of Things (IoT)-based environmental data acquisition system and Artificial Intelligence (AI) models to support solar tracking optimization.  
The system integrates real-time sensor data, cloud-based storage, machine learning models, and a web-based dashboard to predict the Sun’s altitude and azimuth angles.

This work supports the undergraduate thesis:

**“Implementation of an IoT-Based Temperature and Humidity Data Acquisition System for Solar Tracking Optimization Using Artificial Intelligence.”**

---

## 📌 Research Background

The performance of solar panels is strongly influenced by their orientation relative to the Sun. Conventional solar tracking systems rely on astronomical equations or predefined models, which may not fully capture local environmental variations.

This research explores an alternative data-driven approach by utilizing environmental parameters—specifically temperature, humidity, and electrical current—acquired through an IoT system. Machine learning models are then employed to learn temporal patterns and correlations within the data to predict solar position parameters.

---

## 🎯 Research Objectives

- To design an IoT-based system capable of acquiring temperature, humidity, and electrical current data in real time.
- To develop a cloud-based data storage and visualization system for monitoring environmental conditions.
- To implement and evaluate Long Short-Term Memory (LSTM) and Random Forest models for predicting solar altitude and azimuth angles.
- To analyze the limitations of data-driven models compared to conventional astronomical approaches.

---

## 🧠 Methodology Overview

The research methodology consists of the following stages:

1. **Data Acquisition**
   - Environmental data (temperature, humidity, current) collected using sensors connected to an ESP32 microcontroller.
   - Data transmitted via Wi-Fi to a cloud database in real time.

2. **Data Storage and Visualization**
   - Data stored in a cloud-based real-time database.
   - Web-based dashboard developed for monitoring sensor readings and AI prediction results.

3. **Artificial Intelligence Modeling**
   - **LSTM (Long Short-Term Memory):**  
     Used to model temporal dependencies in time-series environmental data.
   - **Random Forest:**  
     Used to capture non-linear relationships between environmental parameters and solar angles.

4. **Prediction Targets**
   - Solar altitude angle
   - Solar azimuth angle

5. **Evaluation**
   - Model performance evaluated using statistical error metrics.
   - Comparison between predictions based on local sensor data and historical weather data from Open-Meteo.

---

## 🏗️ System Architecture

The system consists of four main components:

- **IoT Node**
  - ESP32 microcontroller
  - Temperature and humidity sensors
  - Electrical current sensor

- **Cloud Infrastructure**
  - Real-time database for sensor data and prediction results

- **AI Prediction Service**
  - Python-based service for model inference
  - LSTM and Random Forest models

- **Web Dashboard**
  - Real-time visualization of sensor data
  - Display of predicted solar altitude and azimuth
  - Historical data querying based on timestamp

---

## 📊 Dataset Description

Two main data sources are used in this research:

1. **Local Sensor Data**
   - Temperature (°C)
   - Humidity (%)
   - Electrical current (A)
   - Timestamp (WIB / UTC+7)

2. **Historical Weather Data**
   - Obtained from Open-Meteo Historical Weather API
   - Used as an alternative scenario for model training and evaluation

Only sample datasets are provided in this repository for demonstration purposes.

---

## ⚙️ Technologies Used

- **Hardware**
  - ESP32 Microcontroller
  - Temperature & Humidity Sensor
  - Electrical Current Sensor

- **Software**
  - Python (data processing and AI models)
  - TensorFlow / Keras (LSTM implementation)
  - Scikit-learn (Random Forest)
  - JavaScript, HTML, CSS (Web dashboard)
  - Firebase Realtime Database

---

## 🚀 How to Run the System (Overview)

1. Upload the firmware to the ESP32 to start data acquisition.
2. Configure environment variables for database access.
3. Run the Python prediction service to enable AI inference.
4. Open the web dashboard to monitor sensor data and prediction results.

Detailed step-by-step instructions are provided in the `docs/` directory.

---

## ⚠️ Limitations

- The AI models learn correlations from environmental data rather than using direct astronomical equations.
- Reconstruction of solar azimuth and altitude is less accurate compared to Solar Position Algorithm (SPA) calculations.
- LSTM models require an initial sequence of data before producing stable predictions.
- Prediction accuracy depends on data quality, sampling interval, and environmental variability.

---

## 📚 Academic Note

This repository is intended for educational and research purposes.  
The implementation emphasizes the integration of physics-based instrumentation, IoT systems, and machine learning techniques rather than replacing established astronomical models.

---

## 📄 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this code with proper attribution.

---

## 👤 Author

**Abdulhaqi Hamdi**  
Undergraduate Student in Physics  
Universitas Indonesia