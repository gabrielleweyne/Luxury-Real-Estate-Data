from . import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Favourite(Base):
    __tablename__ = "favourites"
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), unique=True, primary_key=True)
    user = relationship("User")
    estates_ind_id = Column(Integer, ForeignKey("estates_ind.id"), unique=True, primary_key=True)
    estates_ind = relationship("EstatesInd")
    favourited = Column(Integer, default=0)

    def to_view(self):
        return {
            "user_id": self.user_id,
            "estate_source_id": self.estates_ind_id,
            "favourited": self.favourited,
        }
