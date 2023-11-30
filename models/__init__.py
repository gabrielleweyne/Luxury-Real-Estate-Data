print("IMPORTED MODELS")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

user = "root"
password = "root"
mysql = "localhost:3306"
database = "scrap_estates"

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{user}:{password}@{mysql}/{database}?charset=utf8mb4"
)

engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()


def create_models():
    Base.metadata.create_all(bind=engine)
