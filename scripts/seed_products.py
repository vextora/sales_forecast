from sqlalchemy.orm import Session
from tqdm import tqdm
from faker import Faker
from db.models.products import Product
import random

fake = Faker()

CATEGORIES = ["Laptop", "Smartphone", "Furniture", "Accessory", "Tablet"]

def seed_products(db: Session, num_products: int = 100):
	products = []
	for _ in tqdm(range(num_products), desc="Seeding products"):
		product = Product(
			name = fake.word().capitalize() + " " + fake.word().capitalize(),
			category = random.choice(CATEGORIES),
			price = round(random.uniform(100, 2000), 2),
			stock = random.randint(0, 100),
		)
		db.add(product)
		products.append(product)

	db.commit()
	for data in products:
		db.refresh(data)

	print(f"Seeded {len(products)} products")
	return products