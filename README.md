# IoT-Based Temperature and Humidity Data Acquisition System for Solar Tracking Optimization Using Artificial Intelligence

This repository contains the implementation of an Internet of Things (IoT)-based environmental data acquisition system and Artificial Intelligence (AI) models to predict a sun path.
  
The system integrates real-time sensor data, cloud-based storage, machine learning models, and a web-based dashboard to predict the Sun’s altitude and azimuth angles.

This work is a documentation of my undergraduate physics thesis:

**“IoT-Based Temperature and Humidity Data Acquisition System for Steering the Position of Solar Panels Based on Artificial Intelligence Predictions”**

---

## 📌 Research Background

The performance of solar energy systems is highly dependent on the orientation of solar panels relative to the Sun. Conventional solar tracking systems typically rely on astronomical equations and deterministic models, which accurately describe the Sun’s position based on time and location but do not explicitly incorporate local environmental conditions.

This research explores a complementary approach by utilizing **environmental parameters**, specifically **temperature and humidity**, acquired through an IoT-based data acquisition system. These parameters are used as inputs for **machine learning models** to learn temporal patterns and correlations related to the Sun’s apparent position.

The proposed system does not aim to replace astronomical models but to investigate the potential of **data-driven methods** as an alternative or supporting strategy for solar tracking optimization.

---

## 🎯 Research Objectives

- To design and implement an **IoT-based system** capable of acquiring temperature and humidity data in real time.
- To develop a **data acquisition and storage pipeline** for environmental monitoring.
- To implement **Artificial Intelligence models** (LSTM and Random Forest) for predicting solar altitude and azimuth angles.
- To evaluate the performance and limitations of data-driven predictions compared to conventional astronomical approaches.
- To demonstrate the integration of **instrumentation physics, IoT systems, and AI** in a solar tracking context.

---

## 🧠 Methodology Overview

The research methodology consists of the following stages:

### 1. Data Acquisition
- Temperature and humidity data are collected using sensors connected to an **ESP32 microcontroller**.
- Data are transmitted via Wi-Fi to a cloud-based database in near real time.

### 2. Data Storage and Visualization
- Environmental data are stored in a real-time database.
- A **web-based dashboard** is developed to visualize sensor readings and AI prediction results.

### 3. Artificial Intelligence Modeling
- **Long Short-Term Memory (LSTM):**  
  Used to model temporal dependencies in time-series environmental data.
- **Random Forest:**  
  Used to capture non-linear relationships between environmental parameters and solar position angles.

### 4. Prediction Targets
- Solar altitude angle
- Solar azimuth angle

### 5. Evaluation
- Model performance is evaluated using statistical error metrics.
- Predictions based on local IoT sensor data are compared with predictions based on historical weather data.

---

## 🏗️ System Architecture

The system consists of four main components:

### IoT Node
- ESP32 microcontroller  
- Temperature and humidity sensors  
- Data acquisition and wireless transmission module  

### Cloud Infrastructure
- Real-time database for environmental data storage  

### AI Prediction Service
- Python-based prediction service  
- LSTM and Random Forest models for inference  

### Web Dashboard
- Visualization of temperature and humidity data  
- Visualization of predicted solar altitude and azimuth  
- CSV-based replay mode for simulation and demonstration  

---

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
- Handles data transmission to the cloud database

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