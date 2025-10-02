import pandas as pd
import os
import numpy as np
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session
from sqlalchemy.dialects import postgresql
from sklearn.metrics import mean_squared_error, mean_absolute_error

from db.session import SessionLocal
from db.models import Sale, Forecast

def evaluate_forecast(db: Session, days=30):
	# Cari rentang tanggal overlap antara sales dan forecast
	sales_min, sales_max = db.query(func.min(Sale.date), func.max(Sale.date)).first()
	print(sales_min, sales_max)
	forecast_min, forecast_max = db.query(func.min(Forecast.date), func.max(Forecast.date)).first()
	print(forecast_min, forecast_max)

	if not sales_min or not forecast_min:
		print("Data sales/forecast kosong")
		return

	start_date = max(sales_min, forecast_min)
	end_date = min(sales_max, forecast_max)
	print(start_date, end_date)

	if start_date > end_date:
		print("Tidak ada tanggal yang overlap antara sales dan forecast")
		return

	print(f"Evaluasi dari {start_date} sampai {end_date}")

	# Ambil sales & forecast dengan join
	query = (
		db.query(
			Sale.product_id,
			Sale.date.label("sales_date"),
			Sale.sales.label("actual"),
			Forecast.predicted_sales.label("forecast"),
		)
		.join(
			Forecast,
			(Sale.product_id == Forecast.product_id) &
			(cast(Sale.date, Date) == cast(Forecast.date, Date))
		)
		.filter(Sale.date.between(start_date, end_date))
		.order_by(Sale.product_id, Sale.date)
	)

	# Print SQL lengkap dengan value
	print("\n===== SQL Query =====\n")
	print(query.statement.compile(
		dialect=postgresql.dialect(),
		compile_kwargs={"literal_binds": True}
	))

	df = pd.DataFrame(query.all(), columns=["product_id", "sales_date", "actual", "forecast"])

	if df.empty:
		print("Tidak ada data hasil join. Skip evaluasi.")
		return pd.DataFrame()

	results = []
	for product_id, group in df.groupby("product_id"):
		actual = group["actual"].values
		forecast = group["forecast"].values

		if len(actual) == 0:
			continue

		mae = mean_absolute_error(actual, forecast)
		rmse = np.sqrt(mean_squared_error(actual, forecast))
		#rmse = mean_squared_error(actual, forecast, squared=False)
		mape = (abs((actual - forecast) / actual).mean()) * 100

		results.append({
			"product_id": product_id,
			"MAE": mae,
			"RMSE": rmse,
			"MAPE": mape
		})

	results_df = pd.DataFrame(results)
	print(results_df)

	os.makedirs("results", exist_ok=True)
	results_df.to_csv("results/forecast.csv", index=False)
	print("Hasil evaluasi disimpan di results/forecast.csv")

	return results_df

if __name__ == "__main__":
	db = SessionLocal()
	evaluate_forecast(db, days=30)
	db.close()