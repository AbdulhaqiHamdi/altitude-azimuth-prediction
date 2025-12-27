# ===============================================================
#  PROGRAM PEMROSESAN DATA LINGKUNGAN & PERHITUNGAN PARAMETER FISIKA
#  Termasuk: altitude & azimuth matahari, intensitas radiasi (E_T),
#  luminansi, arus panel surya, serta pembentukan vektor arah matahari.
# ===============================================================

import pandas as pd # Library untuk manipulasi data
import numpy as np # Library untuk komputasi numerik
from pysolar.solar import get_altitude, get_azimuth # Library untuk perhitungan posisi matahari

# 1. Membaca dataset hasil Open-Meteo
# Parsing kolom waktu agar dikenali sebagai tipe datetime
df = pd.read_csv("data/hourly_data.csv", parse_dates=["date"])

# 2. Menentukan lokasi geografis pengamatan (Depok)
lat = -6.4       # Lintang selatan
lon = 106.8186   # Bujur timur

# 3. Menetapkan zona waktu untuk data. Dataset Open-Meteo menggunakan UTC sehingga perlu dikonversi
if df["date"].dt.tz is None:
    df["date"] = df["date"].dt.tz_localize("UTC").dt.tz_convert("Asia/Jakarta")
else:
    df["date"] = df["date"].dt.tz_convert("Asia/Jakarta")

df["timestamp"] = df["date"].astype("int64") // 1e9

# 4. Menghitung sudut altitude dan azimuth menggunakan PySolar. Fungsi get_altitude/get_azimuth menggunakan koordinat & waktu aktual
df["altitude_deg"] = df["date"].apply(lambda t: get_altitude(lat, lon, t))
df["azimuth_deg"] = df["date"].apply(lambda t: get_azimuth(lat, lon, t))

# Konversi ke radian untuk perhitungan trigonometri berikutnya
df["altitude_rad"] = np.radians(df["altitude_deg"])
df["azimuth_rad"] = np.radians(df["azimuth_deg"])

df["azimuth_sin"] = np.sin(df["azimuth_rad"])
df["azimuth_cos"] = np.cos(df["azimuth_rad"])

# 5. Menghitung sudut deklinasi matahari (δ). Rumus deklinasi tahunan berdasarkan hari ke-n dalam setahun
# df["day_of_year"] = df["date"].dt.day_of_year
# df["hour_of_year"] = (df["date"].dt.day_of_year - 1) * 24 + df["date"].dt.hour
# df["declination_deg"] = 23.44 * np.sin(
#     np.deg2rad((360 / 365) * (df["day_of_year"] - 81))
# )

# 6. Menghitung parameter radiasi untuk intensitas total (E_T)
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

# 7. Menghitung radiasi total pada permukaan miring (E_T)
df["E_T"] = (
    df["direct_radiation"]
    + df["diffuse_radiation"] * 0.5 * (1 + root_term)
    + df["shortwave_radiation"] * 0.2 * 0.5 * (1 - root_term)
)

# # 8. Menghitung luminansi cahaya dari irradiansi (E_T). Menggunakan rata-rata luminous efficacy (120 lm/W ≈ 0.0083)
# df["luminance"] = df["E_T"] * 0.0083

# 9. Menghitung arus panel surya berdasarkan radiasi. Konstanta 0.0043 berasal dari persamaan P = η E A
df["current"] = 0.0043 * df["E_T"]

# # 10. Menghitung sudut kemiringan panel β. β diturunkan dari persamaan hubungan arah matahari & panel
# df["beta_rad"] = np.arccos(np.clip(root_term, 0, 1))

# # 11. Membentuk vektor arah matahari: S_vector = (Sx, Sy, Sz). Model vektor koordinat bola → kartesian
# df["Sx"] = np.cos(df["altitude_rad"]) * np.sin(df["azimuth_rad"])
# df["Sy"] = np.cos(df["altitude_rad"]) * np.cos(df["azimuth_rad"])
# df["Sz"] = np.sin(df["altitude_rad"])
# df["S_vector"] = list(zip(df["Sx"], df["Sy"], df["Sz"]))

# # 12. Membentuk vektor normal bidang panel: N_vector
# df["Nx"] = np.sin(df["beta_rad"]) * np.sin(df["azimuth_rad"])
# df["Ny"] = np.sin(df["beta_rad"]) * np.cos(df["azimuth_rad"])
# df["Nz"] = np.sin(df["beta_rad"])
# df["N_vector"] = list(zip(df["Nx"], df["Ny"], df["Nz"]))

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
             "E_T"], #,"day_of_year", "Sx", "Sy", "Sz", "Nx", "Ny", "Nz"],
    inplace=True
)

df.to_csv("data/final_data.csv", index=False) # Simpan ke CSV

print(df.head())