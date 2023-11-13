from fastapi import FastAPI, Cookie
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from typing import Union

# .env
user = "root"
password = "root"
mysql = "localhost:3306"
database = "scrap_estates"

# ========= INIT =========

# Create REST API
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect to DB
engine = create_engine(f"mysql+pymysql://{user}:{password}@{mysql}/{database}?charset=utf8mb4")

templates = Jinja2Templates(directory="templates")

# Create DB session
Sessionlocal = sessionmaker(autoflush=False, bind=engine)
session = Sessionlocal()

# ========= MODEL =========
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    email = Column(String(256), unique=True)
    password = Column(String(256))

# Create models on DB
Base.metadata.create_all(bind=engine)

# ========= CONTROLLER & VIEW =========
# @ -> Access class properties
@app.post("api/users")
def create_user(name: str, email: str, password: str):
    user = User(name=name, email=email, password=password)
    session.add(user)
    session.commit()
    return JSONResponse(content=user_view(user), status_code=201)

@app.post("api/users/login")
def login_user(email: str, password: str):
    user = session.query(User).filter_by(email= email).first()
    if user.password == password:
        resp = JSONResponse(content=user_view(user), status_code=201)
        resp.set_cookie(key='login', value=user.id)
        return resp
    else:
        return JSONResponse(content=user_view(user), status_code=403)

@app.get("api/protected")
def restricted(login: Union[str, None] = Cookie(default=None)):
    user = session.query(User).filter_by(id=login).first()
    if user:
        return JSONResponse({'message': f'WELCOME {user.name}'})
    else:
        return JSONResponse({'message': 'ACCESS FORBIDEN'}, 403)

# ========= VIEW =========
def user_view(user: User):
    return {'id': user.id, 'email': user.email, 'name': user.name}