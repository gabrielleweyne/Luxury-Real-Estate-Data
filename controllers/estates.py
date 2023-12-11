from sqlalchemy import and_, or_, func
from models import session
from models.estate import Estate
from models.favourite import Favourite
from models.estates_ind import EstatesInd


def get_price_range():
    return (
        session.query(
            func.max(Estate.price).label("max"),
            func.min(Estate.price).label("min"),
        )
        .first()
        ._mapping
    )


def get_area_range():
    return (
        session.query(
            func.max(Estate.total_area).label("max"),
            func.min(Estate.total_area).label("min"),
        )
        .first()
        ._mapping
    )


def list(
    user_id: int = None,
    favourited=False,
    max_price=None,
    min_price=None,
    max_area=None,
    min_area=None,
):
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
            Estate.type,
            Estate.district,
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
            Favourite.user_id.label("favourited_user_id"),
            get_recent_estates,
        )
        .join(
            get_recent_estates, get_recent_estates.c.source_id == EstatesInd.source_id
        )
        .join(
            Favourite,
            and_(Favourite.estates_ind_id == EstatesInd.id),
            isouter=True,
        )
        .filter(or_(Favourite.user_id == user_id, Favourite.user_id == None))
    )

    if favourited:
        get_estates_query = get_estates_query.filter(Favourite.favourited == 1)

    if max_area != None:
        get_estates_query = get_estates_query.filter(
            get_recent_estates.c.total_area <= max_area
        )

    if min_area != None:
        get_estates_query = get_estates_query.filter(
            get_recent_estates.c.total_area >= min_area
        )

    if max_price != None:
        get_estates_query = get_estates_query.filter(
            get_recent_estates.c.price <= max_price
        )

    if min_price != None:
        get_estates_query = get_estates_query.filter(
            get_recent_estates.c.price >= min_price
        )

    get_estates_query = get_estates_query.order_by(get_recent_estates.c.timestamp.desc())

    estates = []

    for r in get_estates_query.all():
        estates.append(dict(r._mapping))

    # estates = list(map(lambda r: r._mapping, get_estates_query.all()))
    # liste os imóveis
    return estates
