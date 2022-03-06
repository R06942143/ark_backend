import datetime
from sqlalchemy import Boolean, Column, String
from sqlalchemy.sql.sqltypes import DateTime, Integer
from app.db.base_class import Base


class users(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    userid = Column(String(200), unique=True)
    useraddress = Column(String(200), unique=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100))
    account = Column(String(100))
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now, nullable=False, onupdate=datetime.datetime.now)
