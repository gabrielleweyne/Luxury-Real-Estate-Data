from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:root@localhost:3306/scrap_estates'

def save_to_db(estates_df):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Criar sessão
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)

    # Apenas para quando ler do csv
    # estates_df.drop(columns=['Unnamed: 0'], inplace=True)

    # Colocar os dados no SQL
    print('Loading into database...')
    estates_df.to_sql(name ='lopes', con =engine, if_exists='append', index=False)
    print('Saved data on database!')
