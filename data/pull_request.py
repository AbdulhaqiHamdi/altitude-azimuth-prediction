# ===============================================================
#  PROGRAM PENGAMBILAN DATA LINGKUNGAN MENGGUNAKAN OPEN-METEO API
#  Data mencakup suhu, kelembapan, radiasi matahari, kecepatan angin,
#  serta parameter atmosfer lainnya dalam resolusi harian dan jam-jaman.
# ===============================================================

import openmeteo_requests # Library untuk mengakses Open-Meteo API
import pandas as pd # Library untuk manipulasi data
import requests_cache # Library untuk caching hasil request HTTP
from retry_requests import retry # Library untuk mekanisme retry pada request HTTP

# 1. Inisialisasi sistem request dengan caching dan mekanisme retry
# ===============================================================
cache_session = requests_cache.CachedSession('.cache', expire_after=-1) # CachedSession: menyimpan hasil request agar tidak perlu mengunduh ulang
retry_session = retry(cache_session, retries=5, backoff_factor=0.2) # retry(): mencoba kembali request secara otomatis jika terjadi error jaringan
openmeteo = openmeteo_requests.Client(session=retry_session) # Client(): mengelola request ke Open-Meteo API

# 2. Menentukan endpoint API dan parameter request
# ===============================================================
url = "https://archive-api.open-meteo.com/v1/archive"

params = { 
    "latitude": -6.4, # Parameter geografis (koordinat kota Depok)
    "longitude": 106.8186,
    "start_date": "2020-01-01", # Parameter waktu berupa rentang longitudinal 5 tahun (2020–2025)
    "end_date": "2025-08-10",

    # Variabel harian yang akan diunduh
    "daily": [
        "shortwave_radiation_sum",
        "temperature_2m_mean",
        "relative_humidity_2m_mean",
        "weather_code",
        "daylight_duration",
        "wind_speed_10m_max",
        "surface_pressure_mean"
    ],

    # Variabel jam-jaman yang akan diunduh
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
        "wind_speed_100m",
        "weather_code",
        "shortwave_radiation",
        "direct_radiation",
        "direct_normal_irradiance",
        "diffuse_radiation"
    ],

    # Zona waktu lokasi penelitian
    "timezone": "Asia/Bangkok",
}

# 3. Melakukan request ke Open-Meteo API
# ===============================================================
responses = openmeteo.weather_api(url, params=params)

# Hanya menggunakan response lokasi pertama (Depok)
response = responses[0]

# Debug informasi metadata lokasi (untuk keperluan dokumentasi)
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# 4. Pemrosesan data jam-jaman (Hourly Data)
# ===============================================================
hourly = response.Hourly()

# Setiap indeks Variabel(i) sesuai urutan yang didefinisikan dalam params["hourly"]
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_speed_100m = hourly.Variables(3).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(4).ValuesAsNumpy()
hourly_shortwave_radiation = hourly.Variables(5).ValuesAsNumpy()
hourly_direct_radiation = hourly.Variables(6).ValuesAsNumpy()
hourly_direct_normal_irradiance = hourly.Variables(7).ValuesAsNumpy()
hourly_diffuse_radiation = hourly.Variables(8).ValuesAsNumpy()

# 4.1 Membentuk indeks waktu untuk data hourly
# ===============================================================
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
}

# 4.2 Menyusun seluruh data hourly ke dalam dictionary
# ===============================================================
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_speed_100m"] = hourly_wind_speed_100m
hourly_data["weather_code"] = hourly_weather_code
hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
hourly_data["direct_radiation"] = hourly_direct_radiation
hourly_data["direct_normal_irradiance"] = hourly_direct_normal_irradiance
hourly_data["diffuse_radiation"] = hourly_diffuse_radiation


hourly_dataframe = pd.DataFrame(data=hourly_data) # Konversi ke DataFrame

hourly_dataframe.to_csv("data/hourly_data.csv", index=False) # Export ke CSV
print("Export Hourly Data to CSV Success!")
