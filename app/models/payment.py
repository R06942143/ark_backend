import datetime
from sqlalchemy import Boolean, Column, String
from sqlalchemy.sql.sqltypes import Integer, Text
from app.db.base_class import Base


class Payment(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(String(100), nullable=False)
    transaction_id = Column(String(200), nullable=False)
    create_time = Column(String(200), nullable=False, default=datetime.datetime.now)
    line_id = Column(String(200), nullable=False)
    nft_id = Column(Integer)
    amount = Column(Integer)
    payment_status = Column(String(255))
