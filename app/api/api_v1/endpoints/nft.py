from typing import Any, Optional
import requests
import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from app.api import deps
from uuid import uuid4
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent,
    TemplateSendMessage, ButtonsTemplate, URITemplateAction,
)
from app.api.api_v1.endpoints.line import LineRouter

router = APIRouter(route_class=LineRouter)
baseUrl = "https://nft-api-staging.joyso.io/api/v1/"


@router.get("/", response_model=list[schemas.NftPrint])
def read_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.users = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve items.
    """
    if crud.user.is_superuser(current_user):
        nfts = crud.nft.get_group_by_title(db)
    else:
        nfts = crud.nft.get_multi_by_owner(
            db=db, owner_id=current_user.userid
        )
    return nfts


@router.post("/", response_model=schemas.NftBase)
async def create_item(
    *,
    db: Session = Depends(deps.get_db),
    # item_in: schemas.NftCreate,
    hash: Optional[str] = Form(None),
    title: str = Form(...),
    context: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(True),
    catagory: Optional[str] = Form(None),
    image: UploadFile = File(...),
    uid: int = Form(...),
    address: str = Form(...),
    amount: int = Form(...),
    current_user: models.users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    path = "erc1155"
    txid = str(uuid.uuid4())

    payload = json.dumps({
                "txid": txid,
                "to": address,
                "uid": uid,
                "amount": amount
            })
    r = requests.post(
        baseUrl + path,
        headers=headers,
        data=payload
    )
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="not correct mint informaiton")
    if image.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=415,
                            detail='content type error! Please upload valid image type')
    filename = str(uuid4()) + '.' + image.content_type.split('/')[1]
    with open(settings.IMG_PATH + filename, 'wb+') as f:
        f.write(image.file.read())
        f.close()
    userid = crud.user.get_by_address(db, address = address)
    item_in = schemas.NftCreate
    item_in.hash = hash
    item_in.userid = userid
    item_in.title = title
    item_in.context = context
    item_in.is_active = is_active
    item_in.category = catagory
    item_in.imgurl = settings.IMG_HOST + filename
    item_in.uid = uid
    nft = crud.nft.create_with_owner(
        db=db, obj_in=item_in, owner_id=item_in.userid)
    message = "您mint的 nft(" + title + ") 已經為您存到錢包"
    settings.line_bot_api.push_message(
        userid, TextSendMessage(text=message))
    return nft


@router.put("/", response_model=schemas.NftCreate)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    title: str,
    id: int,
    context: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(True),
    catagory: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: models.users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update items.
    """
    nft = crud.nft.get(db=db, id = id)
    if not nft:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item_in = schemas.NftBulkUpdate(**jsonable_encoder(nft))
    if image:
        if image.content_type.split('/')[0] != 'image':
            raise HTTPException(status_code=415,
                                detail='content type error! Please upload valid image type')
        filename = str(uuid4()) + '.' + image.content_type.split('/')[1]
        with open(settings.IMG_PATH + filename, 'wb+') as f:
            f.write(image.file.read())
            f.close()
        item_in.imgurl = settings.IMG_HOST + filename
    if title:
        item_in.title = title
    if context:
        item_in.context = context
    if is_active:
        item_in.is_active = is_active
    if catagory:
        item_in.category = catagory

    
    nft = crud.nft.update_bulk_title(db=db, db_obj_list=nft, obj_in=item_in)
    return nft


@router.put("/{id}", response_model=schemas.NftCreate)
def update_item(
    *,
    db: Session = Depends(deps.get_db),
    title: Optional[str] = Form(None),
    id: int,
    context: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(True),
    catagory: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: models.users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    nft = crud.nft.get(db=db, id=id)
    if not nft:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (nft.userid != current_user.userid):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item_in = schemas.NftUpdate(**jsonable_encoder(nft))
    if image:
        if image.content_type.split('/')[0] != 'image':
            raise HTTPException(status_code=415,
                                detail='content type error! Please upload valid image type')
        filename = str(uuid4()) + '.' + image.content_type.split('/')[1]
        with open(settings.IMG_PATH + filename, 'wb+') as f:
            f.write(image.file.read())
            f.close()
        item_in.imgurl = settings.IMG_HOST + filename
    if title:
        item_in.title = title
    if context:
        item_in.context = context
    item_in.is_active = is_active
    if catagory:
        item_in.category = catagory
    nft = crud.nft.update(db=db, db_obj=nft, obj_in=item_in)
    return nft


@router.get("/{id}", response_model=schemas.NftCreate)
def read_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    nft = crud.nft.get(db=db, id=id)
    if not nft:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (nft.userid != current_user.userid):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return nft


@router.post("/title")
def read_user_by_title(
    *,
    db: Session = Depends(deps.get_db),
    title: str,
    skip: int = 0,
    limit: int = 100,
    current_user: models.users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by title.
    """
    nft = crud.nft.get_user_by_title(db=db, title=title, skip=skip, limit=limit)
    if not nft:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (nft.userid != current_user.userid):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return nft


@router.delete("/{id}", response_model=schemas.NftCreate)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    nft = crud.nft.get(db=db, id=id)
    if not nft:
        raise HTTPException(status_code=404, detail="Item not found")
    if not crud.user.is_superuser(current_user) and (nft.userid != current_user.userid):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    nft = crud.nft.remove(db=db, id=id)
    return nft
