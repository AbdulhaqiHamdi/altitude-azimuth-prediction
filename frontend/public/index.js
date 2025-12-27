// =====================================================
// IoT Dashboard Script (No Login)
// Data: Temperature, Humidity, Current
// Prediction: Altitude & Azimuth (LSTM & RF)
// =====================================================

// ----------------------
// DOM ELEMENTS
// ----------------------
const el = {
  temp: document.getElementById("temperature-value"),
  hum: document.getElementById("humidity-value"),
  current: document.getElementById("current-value"),
  tempStatus: document.getElementById("temp-status"),
  humStatus: document.getElementById("humid-status"),
  lastUpdate: document.getElementById("last-update"),
  currentStatus: document.getElementById("current-status"),


  dashboard: document.getElementById("dashboard-page"),
  info: document.getElementById("info-page"),
  title: document.getElementById("page-title"),
  navLinks: document.querySelectorAll(".nav-link"),
};
let DATA_MODE = "simulation"; // default mode
const CSV_PATH = "data/dummy_data.csv";

// ----------------------
// CSV REPLAY CONFIG
// ----------------------
const CSV_REPLAY_INTERVAL_MS = 5000; // interval simulasi (ms)
let csvReplayStartTime = null;       // waktu mulai replay

// ----------------------
// CHART VARIABLES
// ----------------------
let tempChart;
let humChart;
let currChart;
let altitudeChart;
let azimuthChart;
let csvData = [];
let csvIndex = 0;

const MAX_POINTS = 12;

// ----------------------
// CSV & MODE STATE
// ----------------------
async function loadCSVData() {
  const response = await fetch(CSV_PATH);
  const text = await response.text();

  const rows = text.trim().split("\n");
  const headers = rows[0].split(",");

  csvData = rows.slice(1).map(row => {
    const values = row.split(",");
    let obj = {};
    headers.forEach((h, i) => {
      obj[h] = isNaN(values[i]) ? values[i] : Number(values[i]);
    });
    return obj;
  });
}

function getSimulatedTimestamp(index) {
  if (!csvReplayStartTime) {
    csvReplayStartTime = new Date();
  }

  const t = new Date(
    csvReplayStartTime.getTime() + index * CSV_REPLAY_INTERVAL_MS
  );

  return t.toLocaleTimeString();
}

function generateSimulatedData() {
  return {
    timestamp: new Date().toLocaleTimeString(),
    temperature: 24 + Math.random() * 4,
    humidity: 45 + Math.random() * 15,
    current: 1.2 + Math.random() * 0.5,
    lstm_alt: 35 + Math.random() * 5,
    rf_alt: 35 + Math.random() * 5,
    lstm_azi: 120 + Math.random() * 10,
    rf_azi: 120 + Math.random() * 10
  };
}

// ----------------------
// NAVIGATION HANDLER
// ----------------------
function handleNavigation(page) {
  if (page === "dashboard") {
    el.dashboard.classList.remove("hidden");
    el.info.classList.add("hidden");
    el.title.textContent = "Dashboard";
  } else if (page === "info") {
    el.dashboard.classList.add("hidden");
    el.info.classList.remove("hidden");
    el.title.textContent = "System Info";
  }
  el.navLinks.forEach(link => {
    link.classList.toggle("active-page", link.dataset.page === page);
  });
}

// ----------------------
// INIT ENVIRONMENTAL CHARTS
// ----------------------
function initEnvironmentalCharts() {
  tempChart = new Chart(
    document.getElementById("temperatureChart"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: "Temperature (°C)",
          data: [],
          borderColor: "#ef4444",
          tension: 0.4
        }]
      },
      options: { responsive: true }
    }
  );

  humChart = new Chart(
    document.getElementById("humidityChart"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: "Humidity (%)",
          data: [],
          borderColor: "#3b82f6",
          tension: 0.4
        }]
      },
      options: { responsive: true }
    }
  );

  currChart = new Chart(
    document.getElementById("currentChart"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: "Current (A)",
          data: [],
          borderColor: "#10b981",
          tension: 0.4
        }]
      },
      options: { responsive: true }
    }
  );
}

// ----------------------
// INIT PREDICTION CHARTS
// ----------------------
function initPredictionCharts() {
  altitudeChart = new Chart(
    document.getElementById("altitudeChart"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "LSTM Altitude (°)",
            data: [],
            borderColor: "#8b5cf6",
            tension: 0.4
          },
          {
            label: "RF Altitude (°)",
            data: [],
            borderColor: "#22c55e",
            tension: 0.4
          }
        ]
      },
      options: { responsive: true }
    }
  );

  azimuthChart = new Chart(
    document.getElementById("azimuthChart"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "LSTM Azimuth (°)",
            data: [],
            borderColor: "#f97316",
            tension: 0.4
          },
          {
            label: "RF Azimuth (°)",
            data: [],
            borderColor: "#0ea5e9",
            tension: 0.4
          }
        ]
      },
      options: { responsive: true }
    }
  );
}

// ----------------------
// RESET CHARTS & CSV STATE
// ----------------------
function resetCharts() {
  [tempChart, humChart, currChart, altitudeChart, azimuthChart].forEach(chart => {
    if (!chart) return;
    chart.data.labels = [];
    chart.data.datasets.forEach(ds => ds.data = []);
    chart.update();
  });
}

function resetCSVState() {
  csvIndex = 0;
  csvReplayStartTime = null;
}

// ----------------------
// UPDATE SENSOR DATA
// (SIMULATION – replace with Firebase/API)
// ----------------------
function updateSensorData() {
  const temperature = 24 + Math.random() * 4;
  const humidity = 45 + Math.random() * 15;
  const current = 1.2 + Math.random() * 0.5;

  el.temp.textContent = temperature.toFixed(1);
  el.hum.textContent = humidity.toFixed(1);
  el.lastUpdate.textContent = new Date().toLocaleString();

  el.tempStatus.textContent =
    temperature > 30 ? "High Temperature" : "Normal Temperature";
  el.humStatus.textContent =
    humidity > 70 ? "High Humidity" : "Normal Humidity";

  const label = new Date().toLocaleTimeString();

  tempChart.data.labels.push(label);
  tempChart.data.datasets[0].data.push(temperature);
  humChart.data.labels.push(label);
  humChart.data.datasets[0].data.push(humidity);
  currChart.data.labels.push(label);
  currChart.data.datasets[0].data.push(current);

  [tempChart, humChart, currChart].forEach(chart => {
    if (chart.data.labels.length > MAX_POINTS) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    chart.update();
  });
}

// ----------------------
// UPDATE PREDICTION DATA
// (SIMULATION – replace with AI backend)
// ----------------------
function updatePredictionData() {
  const label = new Date().toLocaleTimeString();

  const lstmAlt = 35 + Math.random() * 5;
  const rfAlt = 35 + Math.random() * 5;

  const lstmAzi = 120 + Math.random() * 10;
  const rfAzi = 120 + Math.random() * 10;

  altitudeChart.data.labels.push(label);
  altitudeChart.data.datasets[0].data.push(lstmAlt);
  altitudeChart.data.datasets[1].data.push(rfAlt);

  azimuthChart.data.labels.push(label);
  azimuthChart.data.datasets[0].data.push(lstmAzi);
  azimuthChart.data.datasets[1].data.push(rfAzi);

  if (altitudeChart.data.labels.length > MAX_POINTS) {
    altitudeChart.data.labels.shift();
    altitudeChart.data.datasets.forEach(d => d.data.shift());
    azimuthChart.data.labels.shift();
    azimuthChart.data.datasets.forEach(d => d.data.shift());
  }

  altitudeChart.update();
  azimuthChart.update();
}

// ----------------------
// RENDER DASHBOARD UNIVERSAL
// ----------------------
function renderDashboard(d) {
  el.temp.textContent = d.temperature.toFixed(1);
  el.hum.textContent = d.humidity.toFixed(1);
  el.current.textContent = d.current.toFixed(2);
  el.lastUpdate.textContent = d.timestamp;

  el.tempStatus.textContent =
    d.temperature > 30 ? "High Temperature" : "Normal Temperature";
  el.humStatus.textContent =
    d.humidity > 70 ? "High Humidity" : "Normal Humidity";
  el.currentStatus.textContent =
    d.current > 2 ? "High Current" : "Normal Current";

  tempChart.data.labels.push(d.timestamp);
  tempChart.data.datasets[0].data.push(d.temperature);

  humChart.data.labels.push(d.timestamp);
  humChart.data.datasets[0].data.push(d.humidity);

  currChart.data.labels.push(d.timestamp);
  currChart.data.datasets[0].data.push(d.current);

  [tempChart, humChart, currChart].forEach(chart => {
    if (chart.data.labels.length > MAX_POINTS) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    chart.update();
  });

  altitudeChart.data.labels.push(d.timestamp);
  altitudeChart.data.datasets[0].data.push(d.lstm_alt);
  altitudeChart.data.datasets[1].data.push(d.rf_alt);

  azimuthChart.data.labels.push(d.timestamp);
  azimuthChart.data.datasets[0].data.push(d.lstm_azi);
  azimuthChart.data.datasets[1].data.push(d.rf_azi);

  if (altitudeChart.data.labels.length > MAX_POINTS) {
    altitudeChart.data.labels.shift();
    altitudeChart.data.datasets.forEach(ds => ds.data.shift());
    azimuthChart.data.labels.shift();
    azimuthChart.data.datasets.forEach(ds => ds.data.shift());
  }

  altitudeChart.update();
  azimuthChart.update();
}

// ----------------------
// DISPATCHER DATA (CSV vs Simulation)
// ----------------------
function updateDashboardData() {
  let data;

  if (DATA_MODE === "csv") {
    if (csvData.length === 0) return;

    // Loop CSV replay
    if (csvIndex >= csvData.length) {
      csvIndex = 0;
      csvReplayStartTime = null; // reset waktu simulasi
    }

    const raw = csvData[csvIndex];

    data = {
      ...raw,
      timestamp: getSimulatedTimestamp(csvIndex)
    };

    csvIndex++;
  }

  if (DATA_MODE === "simulation") {
    data = generateSimulatedData();
  }

  console.log(`[DATA MODE] ${DATA_MODE.toUpperCase()} – index ${csvIndex}`);

  renderDashboard(data);
}

// ----------------------
// SETUP DATA MODE TOGGLE
// ----------------------
function setupDataModeToggle() {
  const selector = document.getElementById("data-mode");

  selector.addEventListener("change", async (e) => {
    DATA_MODE = e.target.value;

    resetCharts();
    resetCSVState();

    if (DATA_MODE === "csv") {
      await loadCSVData();
    }

    updateDashboardData();
  });
}

// ----------------------
// INITIALIZATION
// ----------------------
window.onload = async () => {
  initEnvironmentalCharts();
  initPredictionCharts();

  // Navigation
  el.navLinks.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      handleNavigation(link.dataset.page);
    });
  });

  setupDataModeToggle();

  if (DATA_MODE === "csv") {
    await loadCSVData();
  }

  updateDashboardData();

  setInterval(updateDashboardData, 5000);
};