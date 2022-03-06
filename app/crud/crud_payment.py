from audioop import add
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.payment import Payment
from app.schemas.payment import PaymentBase, PaymentCreate, PaymentUpdate


class CRUDPayment(CRUDBase[Payment, PaymentBase, PaymentCreate]):
    def get_by_transaction(self, db: Session, *, transaction_id: str) -> Optional[Payment]:
        return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()

payment = CRUDPayment(Payment)
