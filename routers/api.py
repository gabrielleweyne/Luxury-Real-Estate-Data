from fastapi import APIRouter, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy import and_, func
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
from models import session
from models.user import User
from models.estate import Estate
from models.favourite import Favourite
from models.estates_ind import EstatesInd
from controllers import estates as estates_controller


api_routes = APIRouter(prefix="/api")


@api_routes.post("/users")
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
    except SQLAlchemyError:
        # remover aletarções
        session.rollback()
        # resposta de erro
        return JSONResponse({"message": "INVALID DATA"}, status_code=400)


# LOGIN DE USUÁRIO
@api_routes.post("/users/login")
def login_user(email: str, password: str):
    # query para ver se o usuário existe
    user = session.query(User).filter_by(email=email).first()
    # checa se a senha está correta
    if not user or user.password != password:
        # se não, erro de acesso proibido
        return JSONResponse({"message": "INVALID PASSWORD OR EMAIL"}, status_code=403)

    # se está tudo bem, mostrar o usuário e salvar o cookie
    resp = JSONResponse(content=user.to_view(), status_code=201)
    resp.set_cookie(key="login", value=user.id)
    return resp


@api_routes.get("/users/me")
def logged_user(login: Union[str, None] = Cookie(default=None)):
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)
    return JSONResponse(content=user.to_view())


# TESTE DE ACESSO PROTEGIDO
# @api_routes.get("/protected")
# def restricted(login: Union[str, None] = Cookie(default=None)):
#     user = session.query(User).filter_by(id=login).first()
#     if user:
#         return JSONResponse({"message": f"WELCOME {user.name}"})
#     else:
#         return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)


# listagem de imóveis
@api_routes.get("/estates")
def list_estates(
    favourited: bool = False, login: Union[str, None] = Cookie(default=None)
):
    # Validar se o usuário está logado
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)

    output_view = estates_controller.list(favourited)

    # responder os imóveis listados
    return JSONResponse(output_view)


@api_routes.get("/estates/{estate_ind_id}")
def get_estate(estate_ind_id: int, login: Union[str, None] = Cookie(default=None)):
    # Validar se o usuário está logado
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)

    estate_ind = session.query(EstatesInd).filter_by(id=estate_ind_id).first()

    if estate_ind == None:
        return JSONResponse({"message": "ESTATE NOT FOUND"}, 400)

    return JSONResponse(
        {"estateData": list(map(lambda e: e.to_view(), estate_ind.estates))}
    )


@api_routes.post("/favourite")
def favourite_estate(
    estate_ind_id: int,
    favourited: bool,
    login: Union[str, None] = Cookie(default=None),
):
    # Validar se o usuário está logado
    user = session.query(User).filter_by(id=login).first()
    if not user:
        return JSONResponse({"message": "ACCESS FORBIDEN"}, 403)

    favourite = (
        session.query(Favourite)
        .filter_by(user_id=login, estates_ind_id=estate_ind_id)
        .first()
    )

    try:
        if favourite == None:
            favourite = Favourite(
                user_id=user.id,
                estates_ind_id=estate_ind_id,
                favourited=1 if favourited else 0,
            )

            session.add(favourite)
        else:
            favourite.favourited = 1 if favourited else 0
        # salva as alterações
        session.commit()
        # resposta com os dados do favorito
        return JSONResponse(content=favourite.to_view(), status_code=201)
    # se o favorito for inválido
    except SQLAlchemyError:
        # remover aletarções
        session.rollback()
        # resposta de erro
        return JSONResponse({"message": "INVALID DATA"}, status_code=400)
