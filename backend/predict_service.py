# predict_service.py
# pip install firebase-admin tensorflow joblib pandas numpy pytz

import os
import time
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import traceback

import firebase_admin
from firebase_admin import credentials, db
from tensorflow.keras.models import load_model

# ===============================================================
# 1. KONFIGURASI
# ===============================================================
UID = "XXX" # Fill with your Firebase User UID

SERVICE_ACCOUNT = "XXX" # Fill with the path to your Firebase service account JSON file
DATABASE_URL = "XXX" # Fill with your Firebase Realtime Database URL

READINGS_PATH = "XXX" # Fill with the path to your readings in Firebase
PRED_PATH = "XXX" # Fill with the path to your predictions in Firebase

INTERVAL_MINUTES = 20
WINDOW = 20
POLL_INTERVAL = 300
MAX_HISTORY = 1000

# ===============================================================
# 2. INISIALISASI FIREBASE
# ===============================================================
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT)
    firebase_admin.initialize_app(cred, {
        "databaseURL": DATABASE_URL
    })

# ===============================================================
# 3. LOAD MODEL & SCALER (dengan validasi kecil)
# ===============================================================
print("\nLoading models...")

def safe_load(path, loader):
    try:
        m = loader(path)
        print(f"✔ Loaded: {path}")
        return m
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        traceback.print_exc()
        raise

# LSTM
model_lstm_alt = load_model("models/model_lstm_altitude.h5", compile=False)
model_lstm_azi_sin = load_model("models/model_lstm_azimuth_sin.h5", compile=False)
model_lstm_azi_cos = load_model("models/model_lstm_azimuth_cos.h5", compile=False)

# LSTM (no current)
model_lstm_alt_no_current = load_model("models/model_lstm_altitude_no_current.h5", compile=False)
model_lstm_azi_sin_no_current = load_model("models/model_lstm_azimuth_sin_no_current.h5", compile=False)
model_lstm_azi_cos_no_current = load_model("models/model_lstm_azimuth_cos_no_current.h5", compile=False)


# LSTM scalers (perhatikan urutan kolom saat training!)
scaler_lstm = safe_load("models/scaler_lstm_altitude.pkl", joblib.load)
scaler_lstm_azi = safe_load("models/scaler_lstm_azimuth.pkl", joblib.load)
# LSTM scalers (no current)
scaler_lstm_no_current = safe_load("models/scaler_lstm_altitude_no_current.pkl", joblib.load)
scaler_lstm_azi_no_current = safe_load("models/scaler_lstm_azimuth_no_current.pkl", joblib.load)

# RF
model_rf_alt = safe_load("models/model_rf_altitude.pkl", joblib.load)
model_rf_azi_sin = safe_load("models/model_rf_azimuth_sin.pkl", joblib.load)
model_rf_azi_cos = safe_load("models/model_rf_azimuth_cos.pkl", joblib.load)
# RF (no current)
model_rf_alt_no_current = safe_load("models/model_rf_altitude_no_current.pkl", joblib.load)
model_rf_azi_sin_no_current = safe_load("models/model_rf_azimuth_sin_no_current.pkl", joblib.load)
model_rf_azi_cos_no_current = safe_load("models/model_rf_azimuth_cos_no_current.pkl", joblib.load)

# RF scalers
scaler_rf = safe_load("models/scaler_rf_altitude.pkl", joblib.load)
scaler_rf_azi = safe_load("models/scaler_rf_azimuth.pkl", joblib.load)
# RF scalers (no current)
scaler_rf_no_current = safe_load("models/scaler_rf_altitude_no_current.pkl", joblib.load)
scaler_rf_azi_no_current = safe_load("models/scaler_rf_azimuth_no_current.pkl", joblib.load)

print("✔ All models loaded\n")

# ===============================================================
# 4. PREPROCESS FIREBASE DATA  — versi lengkap dengan fitur sin-cos
# ===============================================================
def preprocess_firebase_data(raw):
    if not raw:
        return pd.DataFrame()

    rows = []
    for key, item in raw.items():
        ts = item.get("timestamp", None)
        try:
            ts = int(float(ts))
        except:
            continue

        dt = pd.to_datetime(ts, unit="s", utc=True)

        rows.append({
            "datetime": dt,
            "timestamp": ts,
            "temperature": float(item.get("temperature", np.nan)),
            "humidity": float(item.get("humidity", np.nan)),
            "current": float(item.get("current", np.nan)),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.sort_values("datetime").reset_index(drop=True)

    # WIB features
    df["datetime_wib"] = df["datetime"].dt.tz_convert("Asia/Jakarta")
    df["day_of_year"] = df["datetime_wib"].dt.day_of_year
    df["hour"] = df["datetime_wib"].dt.hour
    df["minute"] = df["datetime_wib"].dt.minute
    df["hour_float"] = df["hour"] + df["minute"] / 60.0
    df["hour_of_year"] = (df["day_of_year"] - 1) * 24 + df["hour"]

    # Siklik fitur
    df["sin_hour"] = np.sin(2 * np.pi * df["hour_float"] / 24)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour_float"] / 24)
    df["sin_day"] = np.sin(2 * np.pi * df["day_of_year"] / 365)
    df["cos_day"] = np.cos(2 * np.pi * df["day_of_year"] / 365)

    return df[[
        "datetime", "timestamp",
        "temperature", "humidity", "current",
        "hour_of_year",
        "sin_hour", "cos_hour",
        "sin_day", "cos_day"
    ]]

# ===============================================================
# 5. AGGREGASI 20 MENIT
# ===============================================================
def aggregate_20min(df):
    if df.empty:
        return df

    df_res = df.set_index("datetime").resample(f"{INTERVAL_MINUTES}T").mean()
    df_res = df_res.dropna(how="all").reset_index()
    df_res["timestamp"] = (df_res["datetime"].astype("int64") // 10**9).astype(int)
    return df_res

# ===============================================================
# 6. SAFE PREDICT HELPERS (dengan logging)
# ===============================================================
def safe_rf_predict(model, scaler, df, features):
    # Pastikan kolom ada
    for c in features:
        if c not in df.columns:
            df[c] = np.nan

    X = df[features].values
    mask = ~np.isnan(X).any(axis=1)
    preds = np.full(len(df), np.nan, dtype=float)

    if not mask.any():
        print("safe_rf_predict: tidak ada baris valid untuk features:", features)
        return preds

    try:
        Xs = scaler.transform(X[mask])
    except Exception as e:
        print("safe_rf_predict: scaler.transform error:", e)
        traceback.print_exc()
        return preds

    try:
        p = model.predict(Xs)
        preds[mask] = p
    except Exception as e:
        print("safe_rf_predict: model.predict error:", e)
        traceback.print_exc()

    print(f"safe_rf_predict -> features={features} | rows_total={len(df)} | valid={mask.sum()}")
    return preds


def safe_lstm_predict(model, scaler, df, features, window):
    # Pastikan kolom ada
    for c in features:
        if c not in df.columns:
            df[c] = np.nan

    X = df[features].values
    mask_row = ~np.isnan(X).any(axis=1)
    preds = np.full(len(df), np.nan, dtype=float)

    if mask_row.sum() < window:
        print(f"safe_lstm_predict: not enough valid rows (need {window}, got {mask_row.sum()}) for features {features}")
        return preds

    # transform only valid rows
    scaled = np.full(X.shape, np.nan, dtype=float)
    try:
        scaled_valid = scaler.transform(X[mask_row])
        scaled[mask_row, :] = scaled_valid
    except Exception as e:
        print("safe_lstm_predict: scaler.transform error:", e)
        traceback.print_exc()
        return preds

    seqs = []
    positions = []
    for end in range(window - 1, len(df)):
        start = end - window + 1
        window_data = scaled[start:end+1]
        # if any NaN inside window -> skip
        if np.isnan(window_data).any():
            continue
        seqs.append(window_data)
        positions.append(end)

    if not seqs:
        print("safe_lstm_predict: no complete windows found")
        return preds

    X_seq = np.array(seqs)
    try:
        y = model.predict(X_seq, verbose=0).flatten()
    except Exception as e:
        print("safe_lstm_predict: model.predict error:", e)
        traceback.print_exc()
        return preds

    for pos, val in zip(positions, y):
        preds[pos] = float(val)

    print(f"safe_lstm_predict -> features={features} | windows={len(seqs)} | predicted_positions={len(positions)}")
    return preds

# ===============================================================
# 7. MAIN PREDICTION LOGIC (revisi sin-cos azimuth)
# ===============================================================
def run_prediction(df):
    if df.empty:
        print("run_prediction: dataframe kosong")
        return []

    # Pastikan semua kolom ada
    required_cols = [
        "temperature", "humidity", "current", "timestamp",
        "hour_of_year", "sin_hour", "cos_hour", "sin_day", "cos_day"
    ]
    for c in required_cols:
        if c not in df.columns:
            df[c] = np.nan

    # ==============================
    # MASK: ADA / TIDAK ADA ARUS
    # ==============================
    mask_has_current = ~df["current"].isna()
    mask_no_current = df["current"].isna()

    print(f"Rows with current: {mask_has_current.sum()} | without current: {mask_no_current.sum()}")

    # ==============================
    # FEATURE SETS
    # ==============================
    RF_FEAT = ["temperature", "humidity", "current", "sin_hour", "cos_hour", "sin_day", "cos_day"]
    RF_FEAT_NO_I = ["temperature", "humidity", "sin_hour", "cos_hour", "sin_day", "cos_day"]

    RF_AZI_FEAT = ["temperature", "humidity", "current", "sin_hour", "cos_hour", "sin_day", "cos_day"]
    RF_AZI_FEAT_NO_I = ["temperature", "humidity", "sin_hour", "cos_hour", "sin_day", "cos_day"]

    LSTM_FEAT = ["temperature", "humidity", "current",  "sin_hour", "cos_hour", "sin_day", "cos_day"]
    LSTM_FEAT_NO_I = ["temperature", "humidity", "sin_hour", "cos_hour", "sin_day", "cos_day"]

    LSTM_AZI_FEAT = ["temperature", "humidity", "current", "sin_hour", "cos_hour", "sin_day", "cos_day"]
    LSTM_AZI_FEAT_NO_I = ["temperature", "humidity", "sin_hour", "cos_hour", "sin_day", "cos_day"]

    N = len(df)

    # ==============================
    # INIT OUTPUT
    # ==============================
    rf_alt = np.full(N, np.nan)
    lstm_alt = np.full(N, np.nan)
    rf_azi = np.full(N, np.nan)
    lstm_azi = np.full(N, np.nan)

    # ==========================================================
    # 1️⃣ PREDIKSI DENGAN ARUS
    # ==========================================================
    if mask_has_current.any():
        sub = df[mask_has_current]

        rf_alt[mask_has_current] = safe_rf_predict(
            model_rf_alt, scaler_rf, sub, RF_FEAT
        )

        lstm_alt[mask_has_current] = safe_lstm_predict(
            model_lstm_alt, scaler_lstm, sub, LSTM_FEAT, WINDOW
        )

        rf_sin = safe_rf_predict(
            model_rf_azi_sin, scaler_rf_azi, sub, RF_AZI_FEAT
        )
        rf_cos = safe_rf_predict(
            model_rf_azi_cos, scaler_rf_azi, sub, RF_AZI_FEAT
        )

        rf_azi[mask_has_current] = (np.degrees(np.arctan2(rf_sin, rf_cos)) + 360) % 360

        lstm_sin = safe_lstm_predict(
            model_lstm_azi_sin, scaler_lstm_azi, sub, LSTM_AZI_FEAT, WINDOW
        )
        lstm_cos = safe_lstm_predict(
            model_lstm_azi_cos, scaler_lstm_azi, sub, LSTM_AZI_FEAT, WINDOW
        )

        lstm_azi[mask_has_current] = (np.degrees(np.arctan2(lstm_sin, lstm_cos)) + 360) % 360

    # ==========================================================
    # 2️⃣ PREDIKSI TANPA ARUS (NO_CURRENT)
    # ==========================================================
    if mask_no_current.any():
        sub = df[mask_no_current]

        rf_alt[mask_no_current] = safe_rf_predict(
            model_rf_alt_no_current, scaler_rf_no_current, sub, RF_FEAT_NO_I
        )

        lstm_alt[mask_no_current] = safe_lstm_predict(
            model_lstm_alt_no_current, scaler_lstm_no_current, sub, LSTM_FEAT_NO_I, WINDOW
        )

        rf_sin = safe_rf_predict(
            model_rf_azi_sin_no_current, scaler_rf_azi_no_current, sub, RF_AZI_FEAT_NO_I
        )
        rf_cos = safe_rf_predict(
            model_rf_azi_cos_no_current, scaler_rf_azi_no_current, sub, RF_AZI_FEAT_NO_I
        )

        rf_azi[mask_no_current] = (np.degrees(np.arctan2(rf_sin, rf_cos)) + 360) % 360

        lstm_sin = safe_lstm_predict(
            model_lstm_azi_sin_no_current, scaler_lstm_azi_no_current, sub, LSTM_AZI_FEAT_NO_I, WINDOW
        )
        lstm_cos = safe_lstm_predict(
            model_lstm_azi_cos_no_current, scaler_lstm_azi_no_current, sub, LSTM_AZI_FEAT_NO_I, WINDOW
        )

        lstm_azi[mask_no_current] = (np.degrees(np.arctan2(lstm_sin, lstm_cos)) + 360) % 360

    # ==========================================================
    # 3️⃣ SUSUN OUTPUT
    # ==========================================================
    results = []
    for i in range(N):
        results.append({
            "timestamp": int(df.iloc[i]["timestamp"]),
            "pred_rf_alt": None if np.isnan(rf_alt[i]) else float(rf_alt[i]),
            "pred_lstm_alt": None if np.isnan(lstm_alt[i]) else float(lstm_alt[i]),
            "pred_rf_azi": None if np.isnan(rf_azi[i]) else float(rf_azi[i]),
            "pred_lstm_azi": None if np.isnan(lstm_azi[i]) else float(lstm_azi[i]),
        })

    return results
# ===============================================================
# 10. WRITE FIREBASE
# ===============================================================
def write_predictions(results):
    pred_ref = db.reference(PRED_PATH)
    if not results:
        print("write_predictions: no results")
        return
    pred_ref.child("latest").set(results[-1])
    history = results[-MAX_HISTORY:]
    pred_ref.child("history").set(history)
    print(f"✔ {len(results)} predictions written\n")



# ===============================================================
# 11. MAIN LOOP
# ===============================================================
def run_once():
    print("\n=== Running Prediction Pipeline ===", datetime.now().isoformat())
    try:
        raw = db.reference(READINGS_PATH).get()
        df = preprocess_firebase_data(raw)
        df = aggregate_20min(df)
        print("Aggregated rows:", len(df))
        results = run_prediction(df)
        results_df = pd.DataFrame(results)
        if results:
            print("Last predictions (sample):")
            for r in results[-5:]:
                print(r)
            write_predictions(results)
        else:
            print("No predictions produced.")
        return results_df
    except Exception as e:
        print("❌ Pipeline Error:", e)
        traceback.print_exc()
        return pd.DataFrame()

if __name__ == "__main__":
    run_once()

run_once().to_csv("debug_aggregated_data.csv", index=False)