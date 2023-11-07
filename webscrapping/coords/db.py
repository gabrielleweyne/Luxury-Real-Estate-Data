from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd  # manipulação de dados

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/scrap_estates"


def save_to_db(estates_df, page=1):
    # Criar um csv para usar durante o desenvolvimento
    estates_df.to_csv(f"cep{page}.csv")
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
    estates_df.to_sql(name="estates", con=engine, if_exists="replace", index=False)
    print("========= Saved estates on database!")


def read_all_from_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    conn = engine.connect()

    return pd.read_sql("select * from estates", conn)
