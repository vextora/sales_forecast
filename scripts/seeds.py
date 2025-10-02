from sqlalchemy.orm import Session
from db.session import SessionLocal
from scripts.seed_products import seed_products
from scripts.seed_sales import seed_sales
from scripts.seed_forecast import seed_forecast

def main(num_products: int = 100, days: int = 300):
	#db: Session = SessionLocal()
	db = SessionLocal()
	try:
		print("Mulai seeding...")

		seed_products(db, num_products=num_products)
		seed_sales(db, num_products=num_products, days=days)
		# seed_forecast(db)

		print("Semua seeding selesai")
	finally:
		db.close()

if __name__ == "__main__":
	main()