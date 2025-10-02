from sqlalchemy.orm import Session
from tqdm import tqdm
from db.models.forecast import Forecast
from db.models.products import Product
import datetime
import random

def seed_forecast(db: Session):
	products = db.query(Product).all()
	forecast_entries = []

	for product in tqdm(products, desc="Seeding forecast"):
		for i in range(7): # contoh: 7 hari ke depan
			date = datetime.date.today() + datetime.timedelta(days=i)
			forecast_entries.append(
				Forecast(
					product_id=product.id,
					date=date,
					predicted_sales=random.randint(5, 25)
				)
			)

	db.bulk_save_objects(forecast_entries)
	db.commit()