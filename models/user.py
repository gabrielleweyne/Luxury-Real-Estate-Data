from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    email = Column(String(256), unique=True)
    password = Column(String(256))
    favourites = relationship("Favourite")

    def to_view(self):
        return {"id": self.id, "email": self.email, "name": self.name}
