from optparse import Option
from typing import Optional
from pydantic import BaseModel


# Shared properties
class NftBase(BaseModel):
    hash: Optional[str] = None
    imgurl: Optional[str] = None
    userid: Optional[str] = None
    title: str
    context: Optional[str] = None
    is_active: Optional[bool] = True
    category: Optional[str] = None
    uid: Optional[str] = None
    id: int

    class Config:
        orm_mode = True


class NftPrint(BaseModel):
    Nft: Optional[NftBase] = None
    count: Optional[int] = None

    class Config:
        orm_mode = True


class NftCreate(NftBase):
    pass


class NftUpdate(NftBase):
    pass


class NftBulkUpdate(BaseModel):
    hash: Optional[str] = None
    imgurl: Optional[str] = None
    userid: Optional[str] = None
    title: str
    context: Optional[str] = None
    is_active: Optional[bool] = True
    category: Optional[str] = None