from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
	POSTGRES_HOST: str
	POSTGRES_DB: str
	POSTGRES_USER: str
	POSTGRES_PASSWORD: str
	POSTGRES_PORT: int = 5432

	@computed_field
	@property
	def SQLALCHEMY_DATABASE_URI(self) -> str:
		return (
			f"postgresql+psycopg2://{self.POSTGRES_USER}:"
			f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
			f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
		)

	class Config:
		env_file = ".env"

settings = Settings()