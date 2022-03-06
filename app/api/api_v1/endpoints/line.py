import uuid
import fastapi
import pymysql
import base64
pymysql.install_as_MySQLdb()
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent,
    TemplateSendMessage, ButtonsTemplate, URITemplateAction,
)
from linebot.exceptions import LineBotApiError
import dataset
import requests
import json
import qrcode
from fastapi.encoders import jsonable_encoder
from random import randrange
from app.schemas import line
from app.core.config import settings
import datetime as dt
from fastapi import APIRouter, FastAPI, Request, Response, Body,Depends
from fastapi.routing import APIRoute
from starlette.types import Message
from app.api import deps
from app import crud, models, schemas
from typing import Callable, List
from uuid import uuid4
from sqlalchemy.orm import Session
from datetime import datetime
import httpx

import pymysql
pymysql.install_as_MySQLdb()

async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {"type": "http.request", "body": body}
    request._receive = receive
 
async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body

async def request_get(url, headers):
    async with httpx.AsyncClient() as client:
       return await client.get(url, headers = headers)

class LineRouter(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:

            log_table = db['log']
            try:
                userid = int(json.loads(base64.b64decode(request.headers['authorization'][7:].split('.')[1]+ '=' * (-len(request.headers['authorization'][7:].split('.')[1]) % 4)).decode('utf-8'))['sub'])
            except:
                if( "/api/v1/line/collection/" or "/api/v1/line/receive/" or "/api/v1/line/shop/" or "/api/v1/line/send" in request.url.path):
                    lineid = request.url.path.split("/")[-1]
                    
                    sql = 'SELECT id, userid FROM users where userid =\'' + lineid + '\''
                    try:
                        userid = int(db.query(sql).next()['id'])
                    except:
                        userid = -1
            
            await set_body(request, await request.body())
            body = await get_body(request)
            body = str(body).replace("\"","\'")
            body = str(body).split('Content-Type: image/')[0]
            ip = request.client.host 
            port = str(request.client.port)
            query = request.url.query
            headers = str(request.headers).replace("\"","\'")
            method = request.method
            
            response: Response = await original_route_handler(request)
            response_body = str(response.body).replace("\"","\'")
            log_table.insert(
                dict(
                    create_time=str(datetime.now()), url_path=request.url.path,
                    headers=headers, request=body, userid=userid,
                    ip=ip+":"+port, method=method, response=response_body,
                    request_query=query
                    )
                )
            return response

        return custom_route_handler


router = APIRouter(route_class=LineRouter)
baseUrl = "https://nft-api-staging.joyso.io/api/v1/"

def check_account(event):
    real_user_id = event.source.user_id
    table = db['users']
    result1 = table.find_one(userid=real_user_id)

    # 都存在db的話
    if result1:
        print('already in db')
        db.close()
        settings.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='很高興再見到您！'))

    # 建立全新使用者
    else:
        # create user account api
        url = 'https://nft-api-staging.joyso.io/api/v1/accounts'

        try:
            profile = settings.line_bot_api.get_profile(real_user_id)
            #print(profile['displayName'])
        except LineBotApiError as e:
            pass
        user_id = event.source.user_id
        data = 'uid=' + user_id
        r = requests.post(url=url, headers=headers, data=data)
        try:
            dict_str = json.loads(r.text)
            user_account = dict_str['account']
            user_address = user_account['address']
        except:
            get_acc_url = 'https://nft-api-staging.joyso.io/api/v1/accounts/'+user_id
            r = requests.get(url=get_acc_url,headers=headers)
            dict_str = json.loads(r.text)
            user_account = dict_str['account']
            user_address = user_account['address']
        # generate qr code from user id
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
        qr.add_data(user_address)
        qr.make(fit=True)
        img_qr = qr.make_image(fill='black', back_color='white')
        filename = "/var/www/ArkCard-Linebot/ArkCard-web/qrcode/" + \
                   real_user_id + '.png'
        img_qr.save(filename)

        # add to db
        data = dict(userid=real_user_id, useraddress=user_address,is_active=1,created_at=dt.datetime.now(),updated_at=dt.datetime.now(),hashed_password='',email='',account='',is_superuser=0)
        table.insert(data)

        db.close()

        settings.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='歡迎加入好友'))


# callback event
@router.post("/callback")
async def callback(request: fastapi.Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    settings.handler.handle(body.decode('utf-8'), signature)
    return 'OK'


# follow event
@settings.handler.add(FollowEvent)
def handle_follow(event):
    # get user id when follow
    check_account(event)

# message handler
@settings.handler.add(MessageEvent, message=TextMessage)
def message(event):
    if '我要發送' in event.message.text:
        button_template_message = ButtonsTemplate(
            title=' ',
            text='點擊並打開收藏的NFT，可以選擇想要發送的NFT給對方！',
            actions=[
                URITemplateAction(
                    label='打開發送頁',
                    uri='https://ark.cards/collect.html?'
                        + event.source.user_id)])
        settings.line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="Receive",
                template=button_template_message))

    elif '我要接收' in event.message.text:

        check_account(event)
        button_template_message = ButtonsTemplate(
            title=' ',
            text='點擊並打開接收頁面，即可分享接收地址給對方！',
            actions=[
                URITemplateAction(
                    label='打開接收頁',
                    uri='https://ark.cards/qr-code.html?' +
                        event.source.user_id)])
        settings.line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="Receive",
                template=button_template_message))

    elif 'NFT商店' in event.message.text:
        button_template_message = ButtonsTemplate(
            title=' ',
            text='點擊並打開NFT商品頁，就可以購買您所想要的NFT商品哦！',
            actions=[
                URITemplateAction(
                    label='打開NFT商品頁',
                    uri='https://ark.cards/shop.html?' +
                        event.source.user_id)])
        settings.line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="Receive",
                template=button_template_message))

    elif 'NFT收藏' in event.message.text:
        button_template_message = ButtonsTemplate(
            title=' ',
            text='點擊並打開收藏的NFT，可以查看收到的NFT！',
            actions=[
                URITemplateAction(
                    label='打開收藏頁',
                    uri='https://ark.cards/collect.html?' +
                        event.source.user_id), ])
        settings.line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="Receive",
                template=button_template_message))
    else:
        button_template_message = ButtonsTemplate(
            title=' ',
            text='更多的服務內容，歡迎請上我們的官網！',
            actions=[
                URITemplateAction(
                    label='ArkCard的官網',
                    uri='https://ark.cards')])
        settings.line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="Receive",
                template=button_template_message))


@router.post("/push/")
def push_text(user, message):
    settings.line_bot_api.push_message(
        user, TextSendMessage(text=message)
    )


# nft collection api
@router.get("/collection/{userid}")
async def collection(userid, db: Session = Depends(deps.get_db)):
    # db connect
    
    url = 'accounts/' + str(userid)  + '/nft_balances'
    r = await request_get(baseUrl + url, headers)
    nft_all = {}
    outcome = r.json()['nft_balances']
    ii = 0
    for i in range(len(outcome)):
        nft_ = crud.nft.get_by_uid(db, uid=outcome[i]['uid'])
        if nft_:
            nft_all[ii] = jsonable_encoder(nft_)
            nft_all[ii]['amount'] = outcome[i]['amount']
            ii+=1

    return nft_all

    table3 = db['nftdrops']
    table2 = db['nft']
    nftdrops = {}
    nft = {}
    nfts_all = {}
    i = 0
    j = 0
    if not table3.find_one(userid=userid) and not table2.find_one(userid=userid):
        db.close()
        return "error: user don't have any nft"

    else:
        results1 = table3.find(userid=userid)
        for item in results1:
            nft_id = item['nftid']
            nftdrops[i] = table2.find_one(id=nft_id)
            i += 1

        results2 = table2.find(userid=userid)
        for item in results2:
            nft[j] = item
            j += 1

        nfts_all[0] = nftdrops
        nfts_all[1] = nft
        return nfts_all
        db.close()


# receive handler
@router.get("/receive/{userid}")
def receive(userid):

    table = db['users']

    table.find_one(userid=userid)
    if not table.find_one(userid=userid):
        db.close()
        return "ERROR: User Not Found"
    else:
        result = table.find_one(userid=userid)
        return {
            "userid": result['userid'], "useraddress": result['useraddress']
        }
    db.close()


# send handler
@router.get("/send/{userid}")
async def send(
    userid: str,
    to: str,
    nftuid: int,
    amount: int,
    db_: Session = Depends(deps.get_db),
    ):
    try:
        to_userid = crud.user.get_by_address(db_, address=to)
    except:
        to_userid = "外部"
    transaction_table = db['transaction']
    txid = str(uuid.uuid4())
    payload = {
        "txid": txid,
        # "contract": "0xe0d9102c88b09369df99b1c126fb2eebc13804f8",
        "contract": "0x8d5a7d8ca33fd9edca4b871cf5fb2a9cb5091505",
        "to": to,
        "uid": nftuid,
        "value": amount
    }
    url = "https://nft-api-staging.joyso.io/api/v1/accounts/Uba38e8903d243cd1bd15d5c27cc6653e/erc1155/safe_transfer_to"
    # r = requests.post(baseUrl + "accounts/" + userid+ "/erc1155/safe_transfer_to" , headers=headers, data=payload)
    r = requests.post(baseUrl + "accounts/" + userid+ "/erc1155/transfer_by_admin" , headers=headers, data=payload)
    # r = requests.post(url , headers=headers, data=payload)
    if r.status_code == 200:
        title = crud.nft.get_by_uid(db_, uid=nftuid).__dict__['title']
        message = "您的NFT : " + title + ", 已劃轉！"
        push_text(userid, message)
        transaction_table.insert({'txid':txid,'tfrom':userid,'to':to_userid,'nft':nftuid,'transaction_at':datetime.now()})
        from_name = settings.line_bot_api.get_profile(userid).as_json_dict()['displayName']
        try:
            to_name = settings.line_bot_api.get_profile(to_userid).as_json_dict()['displayName']
        except:
            to_name = "外部"
        fr = "您給"+ to_name +"的NFT(" + title + "), 已發送成功！"
        to_message = from_name +"給您的NFT("+title+"), 已收到！"
        push_text(userid, fr)
        try:
            push_text(to_userid, to_message)
        except:
            pass
    else:
        # push訊息
        message = "交易失敗！如果有疑問，請洽網站的服務信箱！"
        push_text(userid, message)
        return {'msg': r.content}
    return {'msg': 'OK'}


# shop handler
@router.get("/shop/{userid}")
async def shop(userid:str, db: Session = Depends(deps.get_db)):
    # db connect
    url = 'accounts/U9dc55544ecca3a95b170bdf2a30e3691/nft_balances'
    r = await request_get(baseUrl + url, headers)
    nft_all = {}
    outcome = r.json()['nft_balances']
    ii = 0
    for i in range(len(outcome)):
        nft_ = crud.nft.get_by_uid(db, uid=outcome[i]['uid'])
        if nft_:
            nft_all[ii] = jsonable_encoder(nft_)
            nft_all[ii].pop('userid')
            nft_all[ii].pop('is_active')
            nft_all[ii].pop('uid')
            nft_all[ii].pop('hash')
            nft_all[ii].pop('category')
            nft_all[ii]['amount'] = outcome[i]['amount']
            nft_all[ii]['price'] = '1'
            ii += 1

    return nft_all


    sql = 'SELECT title, id, imgurl, userid FROM arkcard.nft  ' \
          'GROUP BY uid'
    result = db.query(sql)
    rows = {}
    i = 0
    for row in result:
        rows[i] = row
        i += 1
    return rows
    db.close()


@router.get("/transactions")
def transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.users = Depends(deps.get_current_active_superuser),
    ):

    sql = 'SELECT * FROM transaction ORDER BY id Desc ' \
          'limit '+str(skip)+', '+str(limit)+''
    nft_table = db['nft']
    result = db.query(sql)
    rows = []
    for row in result:
        nft_item = nft_table.find_one(uid=row['nft'])
        try:
            row['nft'] = nft_item['title']
        except:
            pass
        rows.append(row)
    db.close()

    return rows
