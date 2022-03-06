from datetime import datetime
from lib2to3.pgen2.token import OP
from typing import Optional
from pydantic import BaseModel


# Shared properties
class PaymentBase(BaseModel):
    id: Optional[str] = None
    order_id: Optional[str] = None
    transaction_id: Optional[str] = None
    create_time: Optional[datetime] = datetime.now()
    line_id: Optional[str] = None
    nft_id: int
    amount: int
    payment_status: Optional[str] = None

    class Config:
        orm_mode = True


class PaymentPrint(BaseModel):
    pass


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    pass
