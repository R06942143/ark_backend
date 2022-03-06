
# from app.models.payment import Payment
# from app.schemas.payment import PaymentCreate, PaymentUpdate
from .crud_user import user
from .crud_nft import nft
from .crud_payment import payment
# For a new basic set of CRUD operations you could just do
from .base import CRUDBase

# payment = CRUDBase[Payment, PaymentCreate, PaymentUpdate](Payment)
