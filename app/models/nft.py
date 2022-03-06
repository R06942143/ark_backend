from sqlalchemy import Boolean, Column, String
from sqlalchemy.sql.sqltypes import Integer
from app.db.base_class import Base


class Nft(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    hash = Column(String(200), unique=True)
    imgurl = Column(String(200))
    userid = Column(String(200))
    title = Column(String(200))
    context = Column(String(200))
    is_active = Column(Boolean(), default=True)
    category = Column(String(100))
    uid = Column(String(200))
