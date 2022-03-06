from audioop import add
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import users
from app.schemas.user import UserBase, UserCreate, UserUpdate


class CRUDUser(CRUDBase[users, UserBase, UserCreate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[users]:
        return db.query(users).filter(users.email == email).first()
    
    def get_by_address(selft, db: Session, *, address: str) -> Optional[str]:
        return db.query(users).filter(users.useraddress == address).first().__dict__['userid']

    def get_by_lineid(selft, db: Session, *, lineid: str) -> Optional[str]:
        return db.query(users).filter(users.userid == lineid).first()

    def get_by_account(self, db: Session, *, account: str) -> Optional[users]:
        return db.query(users).filter(users.account == account).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> users:
        db_obj = users(
            email=obj_in.email,
            userid=obj_in.userid,
            useraddress=obj_in.useraddress,
            is_superuser=obj_in.is_superuser,
            account=obj_in.account,
            is_active=obj_in.is_active,
            hashed_password=get_password_hash(obj_in.hashed_password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: users,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> users:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            # update_data = obj_in.dict()
        if "hashed_password" in update_data:
            hashed_password = get_password_hash(update_data["hashed_password"])
            del update_data["hashed_password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, account: str, password: str
    ) -> Optional[users]:
        user = self.get_by_account(db, account=account)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: users) -> bool:
        return user.is_active

    def is_superuser(self, user: users) -> bool:
        return user.is_superuser


user = CRUDUser(users)
