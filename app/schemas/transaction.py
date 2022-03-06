from pydantic import BaseModel

class TransactionNft(BaseModel):
    id: int
    tfrom: str
    to:str
    nft:str
    trasaction_at:str
