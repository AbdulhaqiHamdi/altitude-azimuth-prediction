# ===============================================================
#  PROGRAM PEMROSESAN DATA LINGKUNGAN & PERHITUNGAN PARAMETER FISIKA
#  Termasuk: altitude & azimuth matahari, intensitas radiasi (E_T),
#  luminansi, arus panel surya, serta pembentukan vektor arah matahari.
# ===============================================================

import pandas as pd # Library untuk manipulasi data
import numpy as np # Library untuk komputasi numerik
from pysolar.solar import get_altitude, get_azimuth # Library untuk perhitungan posisi matahari

# Membaca dataset hasil Open-Meteo
# Parsing kolom waktu agar dikenali sebagai tipe datetime
df = pd.read_csv("data/hourly_data.csv", parse_dates=["date"])

# Menentukan lokasi geografis pengamatan (Depok)
lat = -6.4       # Lintang selatan
lon = 106.8186   # Bujur timur

# Menetapkan zona waktu untuk data. Dataset Open-Meteo menggunakan UTC sehingga perlu dikonversi
if df["date"].dt.tz is None:
    df["date"] = df["date"].dt.tz_localize("UTC").dt.tz_convert("Asia/Jakarta")
else:
    df["date"] = df["date"].dt.tz_convert("Asia/Jakarta")

df["timestamp"] = df["date"].astype("int64") // 1e9

# Menghitung sudut altitude dan azimuth menggunakan PySolar. Fungsi get_altitude/get_azimuth menggunakan koordinat & waktu aktual
df["altitude_deg"] = df["date"].apply(lambda t: get_altitude(lat, lon, t))
df["azimuth_deg"] = df["date"].apply(lambda t: get_azimuth(lat, lon, t))

# Konversi ke radian untuk perhitungan trigonometri berikutnya
df["altitude_rad"] = np.radians(df["altitude_deg"])
df["azimuth_rad"] = np.radians(df["azimuth_deg"])

df["azimuth_sin"] = np.sin(df["azimuth_rad"])
df["azimuth_cos"] = np.cos(df["azimuth_rad"])

# Menghitung parameter radiasi untuk intensitas total (E_T)
# sin(2θ) → digunakan dalam reduksi model isotropic sky diffuse
df["sin_double_altitude_rad"] = np.sin(2 * df["altitude_rad"])
sin_2theta = df["sin_double_altitude_rad"]

# Term penyebut (1 + sin(2θ))
denominator = (1 + df["sin_double_altitude_rad"])

# Menjamin input tetap berada dalam domain akar (>=0)
sqrt_input = sin_2theta / denominator
sqrt_input = np.where(sqrt_input < 0, 0, sqrt_input)

# Term akar untuk estimasi β efektif panel surya
root_term = np.sqrt(sqrt_input)

# Menghilangkan informasi zona waktu untuk penyimpanan akhir
df["date"] = df["date"].dt.tz_localize(None)

# Menghitung radiasi total pada permukaan miring (E_T)
df["E_T"] = (
    df["direct_radiation"]
    + df["diffuse_radiation"] * 0.5 * (1 + root_term)
    + df["shortwave_radiation"] * 0.2 * 0.5 * (1 - root_term)
)

# 9. Menghitung arus panel surya berdasarkan radiasi. Konstanta 0.0043 berasal dari persamaan P = η E A
df["current"] = 0.0043 * df["E_T"]

hour = df["date"].dt.hour + df["date"].dt.minute / 60
df["sin_hour"] = np.sin(2 * np.pi * hour / 24)
df["cos_hour"] = np.cos(2 * np.pi * hour / 24)

day = df["date"].dt.day_of_year
df["sin_day"] = np.sin(2 * np.pi * day / 365)
df["cos_day"] = np.cos(2 * np.pi * day / 365)

# 13. Membersihkan kolom dan menyimpan dataset akhir
df.drop(
    columns=["sin_double_altitude_rad",
             "relative_humidity_2m",
             "wind_speed_10m",
             "wind_speed_100m",
             "weather_code",
             "shortwave_radiation",
             "direct_radiation",
             "direct_normal_irradiance",
             "diffuse_radiation",
             "altitude_rad",
             "azimuth_rad",
             "E_T"],
)

df.to_csv("data/final_data.csv", index=False) # Simpan ke CSV

print(df.head())