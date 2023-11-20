from fastapi import FastAPI, Cookie, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, Double, BigInteger, and_, func, create_engine
from sqlalchemy.exc import IntegrityError
from typing import Union
import uvicorn

# .env
user = "root"
password = "root"
mysql = "localhost:3306"
database = "scrap_estates"

# ========= CONEXÃO COM DB E SERVIDOR FAST APÍ =========

# Create REST API
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect to DB
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{mysql}/{database}?charset=utf8mb4"
)

templates = Jinja2Templates(directory="templates")

# Create DB session
Sessionlocal = sessionmaker(autoflush=False, bind=engine)
session = Sessionlocal()

# ========= MODELOS =========
Base = declarative_base()

# Classe do usuário
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    email = Column(String(256), unique=True)
    password = Column(String(256))
    favourites = relationship('Favourite', back_populates="user")
    def to_view(self):
        return {"id": self.id, "email": self.email, "name": self.name}

# Classe de qual usuário favoritou qual imóvel
class Favourite(Base):
    __tablename__ = 'favourite'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates='favourites')
    estate_ind = relationship("EstateInd", back_populates='favourite')
    estate_ind_source_id = Column(String(256), ForeignKey("estates_ind.source_id"))
    favourited = Column(Integer, default=0)

# Classe dos imóveis que foram raspados
class EstateInd(Base):
    __tablename__ = 'estates_ind'
    source_id = Column(String(256))
    favourite = relationship("Favourite", back_populates='estate_ind')
    # Chave primária fora do sql
    estates = relationship("Estate", primaryjoin='EstateInd.source_id == foreign(Estate.source_id)')
    # Chave primária fora do sql
    __mapper_args__ = {
        "primary_key":[source_id]
    }

# Classe de cada raspagem que fez
class Estate(Base):
    # Tabela no SQL
    __tablename__ = "estates"
    # Atributos da classe
    address = Column(String(100))
    dorms = Column(Double())
    lat = Column(Double())
    lng = Column(Double())
    parking = Column(Double())
    price = Column(Double())
    toilets = Column(Double())
    source = Column(String(10))
    source_id = Column(String(256))
    timestamp = Column(String(256))
    total_area  = Column("total area", BigInteger())
    # Chave primária fora do sql, porque o pandas não deixou
    __mapper_args__ = {
        "primary_key":[source_id, timestamp]
    }
    # Transforma no formato correto para visualização externa
    def to_view(self):
        return {
            'address': self.address,
            'dorms': self.dorms,
            'lat': self.lat,
            'lng': self.lng,
            'parking': self.parking,
            'price': self.price,
            'toilets': self.toilets,
            'source': self.source,
            'source_id': self.source_id,
            'timestamp': self.timestamp,
            'total_area': self.total_area
        }


# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# ========= API REST =========
# @ -> Access class properties
@app.post("/api/users")
def create_user(name: str, email: str, password: str):
    # cria o usuário na memória
    user = User(name=name, email=email, password=password)
    # adiciona ele no banco de dados
    session.add(user)
    try:
        # salva as alterações
        session.commit()
        # resposta com os dados do usuário
        return JSONResponse(content=user.to_view(), status_code=201)
    # se o usuário for inválido
    except IntegrityError:
        # remover aletarções
        session.rollback()
        # resposta de erro
        return JSONResponse({'message': 'INVALID DATA'}, status_code=400)

# LOGIN DE USUÁRIO
@app.post("/api/users/login")
def login_user(email: str, password: str):
    # query para ver se o usuário existe
    user = session.query(User).filter_by(email=email).first()
    # checa se a senha está correta
    if not user or user.password != password:
        # se não, erro de acesso proibido
        return JSONResponse({'message': 'INVALID PASSWORD OR EMAIL'}, status_code=403)

    # se está tudo bem, mostrar o usuário e salvar o cookie
    resp = JSONResponse(content=user.to_view(), status_code=201)
    resp.set_cookie(key="login", value=user.id)
    return resp


# TESTE DE ACESSO PROTEGIDO
# @app.get("/api/protected")
# def restricted(login: Union[str, None] = Cookie(default=None)):
#     user = session.query(User).filter_by(id=login).first()
#     if user:
#         return JSONResponse({"message": f"WELCOME {user.name}"})
#     else:
#         return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)

# listagem de imóveis
@app.get('/api/estates')
def list_estates(login: Union[str, None]  = Cookie(default=None)):
    # Validar se o usuário está logado
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)
    
    # subquery para pegar a leitura mais recente dos imóveis
    subquery = session.query(Estate.source_id, func.max(Estate.timestamp).label('timestamp')).group_by(Estate.source_id).subquery()

    # query para pegar os imóveis da subquery
    estates = session.query(Estate).join(subquery, and_(subquery.c.source_id == Estate.source_id, subquery.c.timestamp == Estate.timestamp)).all()

    # responder os imóveis listados
    return JSONResponse(list(map(lambda e: e.to_view(), estates)))

# ========= HTML CONTROLLER =========
@app.get("/login", response_class=HTMLResponse)
def login_page(req: Request):
    return templates.TemplateResponse("login.html", {"request": req, "title": "LOGIN"})

@app.post("/validate", response_class=HTMLResponse)
def validate_page(req: Request, email: str = Form(), password: str = Form()):
    user = session.query(User).filter_by(email=email).first()
    if not user or user.password != password:
        return RedirectResponse("/login")

    resp = RedirectResponse("/estates", 303)
    resp.set_cookie(key="login", value=user.id)
    return resp

@app.get('/estates', response_class=HTMLResponse)
def protected_page(req: Request, login: Union[str, None] = Cookie(default=None)):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return RedirectResponse('/login')
    
    estates = session.query(Estate).all()

    return templates.TemplateResponse("estates.html", {"request": req, "title": "PROTECTED", 'user': user.to_view(), 'estates': estates})

# ========= INICIALIZAR SERVIDOR =========
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)