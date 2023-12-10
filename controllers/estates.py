from sqlalchemy import and_, func
from models import session
from models.estate import Estate
from models.favourite import Favourite
from models.estates_ind import EstatesInd


def list(user_id: int = None, favourited=False):
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
            Estate.district
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
            and_(
                Favourite.estates_ind_id == EstatesInd.id
            ),
            isouter=True,
        )
    )

    if user_id != None:
        get_estates_query = get_estates_query.filter(Favourite.user_id == user_id)

    if favourited:
        get_estates_query = get_estates_query.filter(Favourite.favourited == 1)
    
    estates = []
    
    for r in get_estates_query.all():
        estates.append(dict(r._mapping))

    # estates = list(map(lambda r: r._mapping, get_estates_query.all()))
    # liste os imóveis
    return estates
