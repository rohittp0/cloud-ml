from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Numeric

from config.db import Base


class Token(BaseModel):
    access_token: str
    token_type: str


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    is_admin = Column(Integer, nullable=False, default=False)

    email = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(20), index=False, nullable=True)
    phone = Column(Numeric(10), nullable=False, default=-1)
    picture = Column(String(100), nullable=True)
