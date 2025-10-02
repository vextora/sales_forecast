import argparse
import os

import numpy as np
import pandas as pd
import time
from sqlalchemy.orm import Session

from db.session import SessionLocal
from db.models.sales import Sale
from db.models.products import Product
from db.models.forecast import Forecast

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

# Data Preparation
def prepare_sequences(sales_df, timesteps=30):
    """Siapkan data sequence untuk LSTM"""
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(sales_df[['sales']])

    X, y = [], []
    for i in range(timesteps, len(scaled)):
        X.append(scaled[i-timesteps:i, 0])
        y.append(scaled[i, 0])

    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    return X, y, scaler

# Model Training
def train_lstm(X, y, epochs=10, batch_size=16):
    """Latih model LSTM dengan input sequence"""
    model = Sequential([
        Input(shape=(X.shape[1], 1)),
        LSTM(32, return_sequences=True),
        Dropout(0.2),
        LSTM(16),
        Dense(1) # prediksi single value
    ])

    model.compile(optimizer='adam', loss='mse')

    early_stop = EarlyStopping(
        monitor='loss', patience=3, restore_best_weights=True
    )
    model.fit(
        X, y,
        epochs=epochs,
        batch_size=batch_size,
        verbose=0,
        callbacks=[early_stop]
    )

    return model

# Forecasting
def generate_forecast(model, last_sequence, scaler, steps=30):
    """Generate prediksi ke depan secara autoregressive"""
    forecast = []
    current_seq = last_sequence.copy()

    for _ in range(steps):
        pred = model.predict(
            current_seq.reshape(1, current_seq.shape[0], 1),
            verbose=0
        )
        forecast.append(pred[0, 0])
        # geser sequence
        current_seq = np.append(current_seq[1:], pred[0, 0])

    # balik ke skala asli
    forecast = scaler.inverse_transform(np.array(forecast).reshape(-1, 1))

    return forecast.flatten()

# Main Pipeline
def run_forecast(db: Session, timesteps=30, forecast_days=30):
    products = db.query(Product).all()
    print(f"Total produk: {len(products)}")

    total_start = time.time()

    for idx, product in enumerate(products, start=1):
        print(f"\n[{idx}/{len(products)}] Mulai proses: {product.name} (id={product.id})")
        # Ambil data sales per produk
        sales_records = (
            db.query(Sale)
            .filter(Sale.product_id == product.id)
            .order_by(Sale.date)
            .all()
        )

        if len(sales_records) < timesteps:
            print(f"   ➜ Skip {product.name}, data kurang dari {timesteps}")
            continue

        print(f"   ➜ Data sales ditemukan: {len(sales_records)} records")

        # Buat dataframe untuk preprocessing
        df = pd.DataFrame(
            [(s.date, s.sales) for s in sales_records],
            columns=['date', 'sales']
        )

        # Preprocess
        X, y, scaler = prepare_sequences(df, timesteps=timesteps)

        # Train model
        print(f"   ➜ Training model (X shape: {X.shape}, y shape: {y.shape})")
        start_time = time.time()
        model = train_lstm(X, y, epochs=10, batch_size=16)
        duration = time.time() - start_time
        print(f"   ✓ Training selesai untuk {product.name}")
        print(f"   ✓ Training selesai dalam {duration:.2f} detik (data: {len(sales_records)} records)")

        # Forecast ke depan
        last_seq = X[-1, :, 0]
        preds = generate_forecast(model, last_seq, scaler, steps=forecast_days)

        # Simpan hasil ke DB
        forecast_dates = pd.date_range(
            start=df['date'].iloc[-1] + pd.Timedelta(days=1),
            periods=forecast_days
        )

        for d, p in zip(forecast_dates, preds):
            db.add(Forecast(
                product_id = product.id,
                date = d.date(),
                predicted_sales = float(p)
            ))

        print(f"   ✓ Forecast {forecast_days} hari disimpan untuk {product.name}")

    db.commit()
    print("Forecast selesai")

# Backtest pipeline
def run_backtest(db: Session, timesteps=30, test_days=30, cutoff_date=None):
    products = db.query(Product).all()
    results = []
    print(f"Total produk: {len(products)}")

    for idx, product in enumerate(products, start=1):
        print(f"\n[{idx}/{len(products)}] Backtest: {product.name} (id={product.id})")
        sales_records = (
            db.query(Sale)
            .filter(Sale.product_id == product.id)
            .order_by(Sale.date)
            .all()
        )

        if len(sales_records) < timesteps + test_days:
            print(f"   ➜ Skip {product.name}, data kurang dari {timesteps + test_days}")
            continue

        df = pd.DataFrame(
            [(s.date, s.sales) for s in sales_records],
            columns=['date', 'sales']
        )

        if cutoff_date:
            df_train = df[df['date'] <= cutoff_date]
            df_test = df[df['date'] > cutoff_date].head(test_days)
        else:
            df_train = df.iloc[:-test_days]
            df_test = df.iloc[-test_days:]

        if len(df_train) < timesteps:
            print(f"   ➜ Skip {product.name}, train data terlalu sedikit")
            continue

        X, y, scaler = prepare_sequences(df_train, timesteps=timesteps)
        model = train_lstm(X, y, epochs=10, batch_size=16)

        last_seq = X[-1, :, 0]
        preds = generate_forecast(model, last_seq, scaler, steps=len(df_test))

        # hitung metrik error
        actual = df_test['sales'].values[:len(preds)]
        mae = mean_absolute_error(actual, preds)
        rmse = np.sqrt(mean_squared_error(actual, preds))
        # rmse = mean_squared_error(actual, preds, squared=False)
        mape = (abs((actual - preds) / actual).mean()) * 100

        results.append({
            "product_id": product.id,
            "product_name": product.name,
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape,
        })

        print(f"[Backtest] {product.name}" 
              f"(id={product.id} → "
              f"MAE={mae:.2f}, RMSE={rmse:.2f}, MAPE={mape:.2f}%"
        )

        #df_result = pd.DataFrame({
        #    "date": df_test['date'].values,
        #    "actual": df_test['sales'].values,
        #    "predicted": preds
        #})
        #print(df_result.head())

    results_df = pd.DataFrame(results)
    os.makedirs("../results", exist_ok=True)
    results_df.to_csv("../results/backtest.csv", index=False)
    print("Backtest selesai & hasil disimpan ke results/backtest.csv")

    if not results_df.empty:
        avg_mae = results_df["MAE"].mean()
        avg_rmse = results_df["RMSE"].mean()
        avg_mape = results_df["MAPE"].mean()
        print("\n===== Summary Bactest Semua Produk =====")
        print(f"Rata-rata MAE: {avg_mae:.2f}")
        print(f"Rata-rata RMSE: {avg_rmse:.2f}")
        print(f"Rata-rata MAPE: {avg_mape:.2f}%")
    else:
        print("Tidak ada hasil backtest yang valid")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["forecast", "backtest"], required=True)
    parser.add_argument("--cutoff", type=str, default=None, help="Cutoff date (YYYY-MM-DD untuk backtest")
    args = parser.parse_args()

    db = SessionLocal()
    if args.mode == "forecast":
        run_forecast(db, timesteps=30, forecast_days=30)
    elif args.mode == "backtest":
        cutoff = pd.to_datetime(args.cutoff) if args.cutoff else None
        run_backtest(db, cutoff_date=cutoff)
    db.close()