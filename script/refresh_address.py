import requests
import pymysql

# from app import crud
# from app.api import deps
pymysql.install_as_MySQLdb()
import dataset
import requests
import json
import qrcode

baseUrl = "https://nft-api-staging.joyso.io/api/v1/"

table = db.query('select * from users')
# result1 = table.find_one(userid=real_user_id)
for i in table:
    if i.get('userid'):
        user_id = i.get('userid')
        data = 'uid=' + user_id 
        r = requests.post(url=baseUrl + 'accounts', headers=headers, data=data)

        # extract the account address
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
                    user_id + '.png'
        img_qr.save(filename)
        db.query('update users set useraddress=\"' + str(user_address) + '\" where id=' + str(i.get('id')))