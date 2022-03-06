from pydantic import BaseModel


class TransactionNft(BaseModel):
    nftid: str
    address: str
      
    class Config:
        orm_mode = True

class BuyNft(BaseModel):
    nftid: str 
    userid: str
    amount: int

    class Config:
        orm_mode = True

class NftDrops(BaseModel):
    userid: str
    email: str


class callBack(BaseModel):
    type: str
    data: dict
