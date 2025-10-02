from fastapi import FastAPI

app = FastAPI(title="Stock Forecast App")

@app.get("/")
async def root():
	return {"message": "Hello World"}