from fastapi import APIRouter, Request, Cookie, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, func
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
from models import session
from models import session
from models.user import User
from models.estate import Estate
from models.favourite import Favourite
from models.estates_ind import EstatesInd


templates = Jinja2Templates(directory="templates")

browser_routes = APIRouter()


# ========= HTML CONTROLLER =========
@browser_routes.get("/login", response_class=HTMLResponse)
def login_page(req: Request):
    return templates.TemplateResponse("login.html", {"request": req, "title": "LOGIN"})


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
        "estates.html",
        {
            "request": req,
            "title": "PROTECTED",
            "user": user.to_view(),
            "estates": estates,
        },
    )
