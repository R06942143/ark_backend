from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from sqlalchemy import func
from itertools import groupby
from operator import attrgetter
from pydantic import BaseModel
from app.db.base_class import Base



from app.crud.base import CRUDBase
from app.models.nft import Nft
from app.schemas.nft import NftBase, NftCreate, NftUpdate # noqa

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDNft(CRUDBase[Nft, NftBase, NftCreate]):
    def get_by_uid(
        self, db: Session, *, uid: int
    ) -> list[Nft]:
        return db.query(Nft).filter(Nft.uid == uid).filter(Nft.is_active == True).first()

    def get_by_title(
        self, db: Session, *, title: str
    ) -> list[Nft]:
        return db.query(Nft).filter(Nft.title == title).all()

    def get_multi_by_owner(
        self, db: Session, *, skip: int = 0, limit: int = 100, owner_id: str
    ) -> List[Nft]:
        return db.query(Nft).filter(
            Nft.userid == owner_id).offset(skip).limit(limit).all()

    def get_group_by_title(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Nft]:
        return db.query(Nft, func.count(Nft.userid).label('count'))\
            .group_by(Nft.title).offset(skip).limit(limit).all()

    def get_user_by_title(
        self, db: Session, *, skip: int = 0, limit: int = 100, title: str
    ) -> List[Nft]:
        return db.query(Nft.userid).filter(Nft.title == title, Nft.userid != None)\
            .offset(skip).limit(limit).all() # noqa

    def create_with_owner(
        self, db: Session, *, obj_in: NftCreate, owner_id: str
    ) -> Nft:
        db_obj = Nft(
            hash=obj_in.hash,
            imgurl=obj_in.imgurl,
            userid=owner_id,
            title=obj_in.title,
            context=obj_in.context,
            is_active=obj_in.is_active,
            category=obj_in.category,
            uid = obj_in.uid
            
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_bulk_title(
        self, db: Session, *, db_obj_list: list[NftUpdate],
        obj_in: NftUpdate
    ) -> Nft:
        for db_obj in db_obj_list:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


nft = CRUDNft(Nft)
