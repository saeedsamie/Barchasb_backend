class Settings:
    DATABASE_URL: str = "postgresql://admin:admin@barchasb.bz91.ir:5432/barchasb_db"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
