from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from models import session
from models.user import User
from models.estate import Estate


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
def create_user_page(req: Request, name: str = Form(), email: str = Form(), password: str = Form()):
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
        return RedirectResponse("/login")

    resp = RedirectResponse("/estates", 303)
    resp.set_cookie(key="login", value=user.id)
    return resp


@browser_routes.get("/estates", response_class=HTMLResponse)
def protected_page(req: Request, login: Union[str, None] = Cookie(default=None)):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return RedirectResponse("/login")

    estates = session.query(Estate).all()

    return templates.TemplateResponse(
        "home.html",
        {
            "request": req,
            "title": "PROTECTED",
            "user": user.to_view(),
            "estates": estates,
        },
    )
