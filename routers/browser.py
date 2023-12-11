from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from models import session
from models.user import User
from models.estates_ind import EstatesInd
from controllers import estates as estates_controller

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
    user = session.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        return RedirectResponse("/login", 303)

    resp = RedirectResponse("/estates", 303)
    resp.set_cookie(key="login", value=user.id)
    return resp


@browser_routes.get("/estates", response_class=HTMLResponse)
def estates_page(
    req: Request,
    login: Union[str, None] = Cookie(default=None),
    favourited=False,
    max_area: Union[float, None] = None,
    min_area: Union[float, None] = None,
    max_price: Union[float, None] = None,
    min_price: Union[float, None] = None,
):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return RedirectResponse("/login")

    estates = estates_controller.list(
        login,
        favourited,
        max_price,
        min_price,
        max_area,
        min_area,
    )

    chunks = []

    for i in range(1, len(estates) + 1, 3):
        chunks.append(estates[(i - 1) : (i + 2)])

    return templates.TemplateResponse(
        "home.html",
        {
            "request": req,
            "title": "PROTECTED",
            "user": user.to_view(),
            "estates_chunks": chunks,
            "price_range": estates_controller.get_price_range(),
            "area_range": estates_controller.get_area_range(),
        },
    )


@browser_routes.get("/estates/{estate_ind_id}", response_class=HTMLResponse)
def estate_detail_page(
    req: Request, estate_ind_id: int, login: Union[str, None] = Cookie(default=None)
):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return RedirectResponse("/login")

    estate_ind = session.query(EstatesInd).filter_by(id=estate_ind_id).first()

    return templates.TemplateResponse(
        "estate.html",
        {
            "request": req,
            "title": "PROTECTED",
            "user": user.to_view(),
            "estates_ind": estate_ind,
            "estates": list(map(lambda e: e.to_view(), estate_ind.estates)),
        },
    )


@browser_routes.get("/about", response_class=HTMLResponse)
def estate_detail_page(req: Request):
    # user = session.query(User).filter_by(id=login).first()
    # if not user:
    #     return RedirectResponse("/login")

    return templates.TemplateResponse(
        "sobre.html",
        {"request": req},
    )


@browser_routes.get("/profile", response_class=HTMLResponse)
def estate_detail_page(req: Request, login: Union[str, None] = Cookie(default=None)):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return RedirectResponse("/login")
    estates = estates_controller.list(user_id=login, favourited=True)
    return templates.TemplateResponse(
        "perfil.html",
        {
            "request": req,
            "user": user,
            "estates": estates,
            "estates_length": len(estates),
        },
    )


@browser_routes.get("/heat-map", response_class=HTMLResponse)
def estate_detail_page(req: Request):
    return templates.TemplateResponse(
        "heat_map.html",
        {"request": req, "estates": estates_controller.list()},
    )
