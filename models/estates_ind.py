from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
)


class EstatesInd(Base):
    __tablename__ = "estates_ind"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(256), unique=True)
    favourite = relationship("Favourite")
    estates = relationship("Estate")
