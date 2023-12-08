from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, func
from models import session
from models.user import User
from models.estate import Estate
from models.favourite import Favourite
from models.estates_ind import EstatesInd

templates = Jinja2Templates(directory="templates")

browser_routes = APIRouter()


# ========= HTML CONTROLLER =========
@browser_routes.get("/", response_class=HTMLResponse)
def login_page(req: Request):
    return RedirectResponse("/login", 303)


@browser_routes.get("/login", response_class=HTMLResponse)
def login_page(req: Request):
    return templates.TemplateResponse("login.html", {"request": req, "title": "LOGIN"})


@browser_routes.get("/create-user", response_class=HTMLResponse)
def create_user_page(req: Request):
    return templates.TemplateResponse(
        "login.html", {"request": req, "title": "LOGIN", "create_user": True}
    )


@browser_routes.post("/new-user", response_class=HTMLResponse)
def create_user_page(
    req: Request, name: str = Form(), email: str = Form(), password: str = Form()
):
    user = User(name=name, email=email, password=password)
    # adiciona ele no banco de dados
    session.add(user)
    try:
        # salva as alterações
        session.commit()
        # resposta com os dados do usuário
        return RedirectResponse("/login", 303)
    # se o usuário for inválido
    except SQLAlchemyError:
        # remover aletarções
        session.rollback()
        # resposta de erro
        return RedirectResponse("/create-user", 303)


@browser_routes.post("/validate", response_class=HTMLResponse)
def validate_page(req: Request, email: str = Form(), password: str = Form()):
    user = session.query(User).filter_by(email=email).first()
    if not user or user.password != password:
        return RedirectResponse("/login", 303)

    resp = RedirectResponse("/estates", 303)
    resp.set_cookie(key="login", value=user.id)
    return resp


@browser_routes.get("/estates", response_class=HTMLResponse)
def estates_page(req: Request, login: Union[str, None] = Cookie(default=None), favourited=False):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return RedirectResponse("/login")

    # subquery para pegar a leitura mais recente dos imóveis
    most_recent_reading = (
        session.query(Estate.source_id, func.max(Estate.timestamp).label("timestamp"))
        .group_by(Estate.source_id)
        .subquery()
    )

    # subquery para pegar o imóvel correspondente da leitura mais recente
    get_recent_estates = (
        session.query(Estate)
        .join(
            most_recent_reading,
            and_(
                most_recent_reading.c.source_id == Estate.source_id,
                most_recent_reading.c.timestamp == Estate.timestamp,
            ),
        )
        .subquery()
    )

    # adiciona informação se o imóvel já foi favoritado pelo usuário
    get_estates_query = (
        session.query(
            EstatesInd.id.label("estates_ind_id"),
            Favourite.favourited.label("favourited"),
            get_recent_estates,
        )
        .join(
            get_recent_estates, get_recent_estates.c.source_id == EstatesInd.source_id
        )
        .join(
            Favourite,
            and_(Favourite.estates_ind_id == EstatesInd.id, Favourite.user_id == login),
            isouter=True,
        )
    )

    if favourited:
        get_estates_query = get_estates_query.filter(Favourite.favourited == 1)

    # liste os imóveis
    estates = list(map(lambda r: dict(r._mapping), get_estates_query.all()))

    chunks = []

    for i in range(1, len(estates) + 1, 3):
        chunks.append(estates[(i-1):(i+2)])

    return templates.TemplateResponse(
        "home.html",
        {
            "request": req,
            "title": "PROTECTED",
            "user": user.to_view(),
            "estates_chunks": chunks,
        },
    )
