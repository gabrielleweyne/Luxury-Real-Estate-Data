from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd  # manipulação de dados

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/scrap_estates"


def save_to_db(estates, page=1):
    # Transformar em um dataframe
    df = pd.DataFrame(estates)
    # Criar um csv para usar durante o desenvolvimento
    df.to_csv(f"reports/lopes_imoveis{page}.csv")
    # df = pd.read_csv(f"lopes_imoveis{page}.csv")

    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Criar sessão
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)

    # Apenas para quando ler do csv
    # estates_df.drop(columns=['Unnamed: 0'], inplace=True)

    # Colocar os dados no SQL
    print("========= Loading into database...")
    df.to_sql(name="lopes", con=engine, if_exists="append", index=False)
    print("========= Saved estates on database!")
