import dataset
import uuid
from datetime import datetime
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent,
    TemplateSendMessage, ButtonsTemplate, URITemplateAction,
)
from fastapi import APIRouter
from fastapi.param_functions import Depends
from linepay import LinePayApi
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from app import crud, schemas
from app.api import deps
from fastapi.encoders import jsonable_encoder
import requests
from app.core.config import settings


baseUrl = "https://nft-api-staging.joyso.io/api/v1/"

# template
templates = Jinja2Templates(directory="templates")

router = APIRouter()



HOST_NAME = "https://api.ptt.cx:8750"
# Line Pay Config
LINE_PAY_CHANNEL_ID = LINE_PAY_CHANNEL_ID
LINE_PAY_CHANNEL_SECRET = ""
LINE_PAY_REQEST_BASE_URL = "https://api.ptt.cx:8750/api/v1/linepay"
line = LinePayApi(
    LINE_PAY_CHANNEL_ID, LINE_PAY_CHANNEL_SECRET, is_sandbox=True
)

# CACHE
CACHE = {}

def push_text(user, message):
    settings.line_bot_api.push_message(
        user, TextSendMessage(text=message)
    )
# Request
@router.post('/request')
async def pay_request(
        line_id:str, nft_id: str, amount: int,
        db: Session = Depends(deps.get_db)
    ):
    order_id = str(uuid.uuid4())
    currency = "TWD"
    nft = crud.nft.get(db=db, id=nft_id)
    
    request_options = {
        "amount": amount,
        "currency": currency,
        "orderId": order_id,
        "packages": [
            {
                "id": nft.id,
                "amount": amount,
                "products": [
                    {
                        "name": nft.title,
                        "quantity": amount,
                        "price": 1,
                        "imageUrl": nft.imgurl
                    }
                ]
            }

        ],
        "redirectUrls": {
            "confirmUrl": "https://ark.cards/confirm.html",
            "cancelUrl" : "https://ark.cards/confirm.html"
        }
    }

    response = line.request(request_options)
    transaction_id = int(response.get("info", {}).get("transactionId", 0))
    check_result = line.check_payment_status(transaction_id)
    response["transaction_id"] = transaction_id
    response["paymentStatusCheckReturnCode"] = check_result.get(
        "returnCode", None
    )
    response["paymentStatusCheckReturnMessage"] = check_result.get(
        "returnMessage", None
    )
    payment_obj = schemas.payment.PaymentBase(
        order_id=order_id, transaction_id=transaction_id,
        amount=amount, nft_id=nft_id,
        payment_status="establish the order", line_id=line_id
    )
    payment = crud.payment.create(db=db, obj_in=payment_obj)

    return {"web":response["info"]["paymentUrl"]['web'], "app":response["info"]["paymentUrl"]['web']}
    return response["info"]["paymentUrl"]


# Confirm
@router.get('/confirm')
async def pay_confirm(
    transactionId: int = 123456789,
    db: Session = Depends(deps.get_db)
):

    transaction_table = db_['transaction']
    payment = crud.payment.get_by_transaction(db, transaction_id=transactionId)
    response = line.confirm(
        transactionId, float(payment.amount), "TWD")
    check_result = line.check_payment_status(transactionId)
    payment_details = line.payment_details(transaction_id=transactionId)
    response["transaction_id"] = transactionId
    response["paymentStatusCheckReturnCode"] = check_result.get(
        "returnCode", None
    )
    response["paymentStatusCheckReturnMessage"] = check_result.get(
        "returnMessage", None
    )
    response["payment_details"] = payment_details
    if(response["paymentStatusCheckReturnCode"] == '0123'):
        to = crud.user.get_by_lineid(db, lineid=payment.line_id).__dict__['useraddress']
        payload = {
            "txid": transactionId,
            "contract": "0x8d5a7d8ca33fd9edca4b871cf5fb2a9cb5091505",
            "to": to,
            "uid": crud.nft.get(db, id=payment.nft_id).__dict__['uid'],
            "value": payment.amount
        }
        r = requests.post(baseUrl + "accounts/lineid/erc1155/transfer_by_admin",
                        headers=headers, data=payload)
        payment_update = schemas.payment.PaymentUpdate(**jsonable_encoder(payment))
        if r.status_code == 200:
            title = crud.nft.get(db, id=payment.nft_id).__dict__['title']
            message = "您的NFT : " + title + ", 已劃轉！"
            push_text("lineid", message)
            transaction_table.insert({'txid':transactionId,'tfrom':"lineid",'to':payment.line_id,'nft':crud.nft.get(db, id=payment.nft_id).__dict__['uid'],'transaction_at':datetime.now()})
            from_name = settings.line_bot_api.get_profile("lineid").as_json_dict()['displayName']
            try:
                to_name = settings.line_bot_api.get_profile(payment.line_id).as_json_dict()['displayName']
            except:
                to_name = "外部"
            fr = "您賣給"+ to_name +"的NFT(" + title + "), 已發送，請靜待網路確認！"
            to_message = "您購買的NFT("+title+"), 已成功，請靜待網路確認！"
            push_text("U9dc55544ecca3a95b170bdf2a30e3691", fr)
            try:
                push_text(payment.line_id, to_message)
            except:
                pass
            payment_update.payment_status = "success"
            crud.payment.update(db, db_obj=payment, obj_in=payment_update)
            return "OK"
        else:
            # push訊息
            payment_update.payment_status = "success get payment, but transfer failed, error message is" + r.content
            crud.payment.update(db, db_obj=payment, obj_in=payment_update)
            message = str(transactionId) + " 收款成功，轉移失敗， error message is" + r.content
            to_message = str(transactionId)+ " 收款成功，轉移失敗，請洽客服"
            try:
                push_text(payment.line_id, to_message)
            except:
                pass
            push_text("lineid", message)
            return {'msg': "收款成功，轉移失敗，請洽客服"}
    else:
        payment_update = schemas.payment.PaymentUpdate(**jsonable_encoder(payment))
        payment_update.payment_status = "cancel"
        crud.payment.update(db, db_obj=payment, obj_in=payment_update)
        return "交易取消"