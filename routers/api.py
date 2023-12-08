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

    # subquery para pegar a leitura mais recente dos imóveis
    most_recent_reading = (
        session.query(Estate.source_id, func.max(Estate.timestamp).label("timestamp"))
        .group_by(Estate.source_id)
        .subquery()
    )

    # subquery para pegar o imóvel correspondente da leitura mais recente
    get_recent_estates = (
        session.query(
            Estate.address,
            Estate.dorms,
            Estate.lat,
            Estate.lng,
            Estate.parking,
            Estate.price,
            Estate.toilets,
            Estate.source,
            Estate.source_id,
            Estate.timestamp,
            Estate.total_area,
            Estate.estates_ind_id,
            Estate.img,
        )
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
    estates = get_estates_query.all()

    output_view = list(map(lambda r: dict(r._mapping), estates))

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
                favourited=1 if favourite else 0,
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
