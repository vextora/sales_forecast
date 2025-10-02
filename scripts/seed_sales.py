import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from tqdm import tqdm
from db.models.products import Product
from db.models.sales import Sale

np.random.seed(42)

def seed_sales(db: Session, num_products: int = 300, days: int = 300):
	products = db.query(Product).limit(num_products).all()
	dates = pd.date_range(start="2025-01-01", periods=days)
	#dates = pd.date_range(start="2025-01-01", end="2025-12-15")

	sales_entries = []
	for product in tqdm(products, desc="Seeding sales"):
		base_demand = np.random.randint(5, 20)
		for date in dates:
			season = 2 * np.sin(2 * np.pi * date.dayofyear / 30)
			noise = np.random.randn()
			sales_value = max(0, base_demand + season + noise)
			sales_entries.append(
				Sale(product_id=product.id, date=date.date(), sales=float(sales_value))
			)

	db.bulk_save_objects(sales_entries)
	db.commit()
	print(f"Seeded sales for {len(products)} products ({len(sales_entries)} rows)")