import time
from urllib.parse import quote_plus

import requests

def login():
    loginStartTime = time.time()
    loginDatas = requests.post("https://api.tomato-aoarasi.com/phi-login/login", data="Browser").json()
    qrCodeUrl = f"https://tool.oschina.net/action/qrcode/generate?data={quote_plus(loginDatas["qrcode_url"])}&output=image/png&error=M&type=0&margin=4&size=4"
    print(qrCodeUrl)
    while True:
        if time.time() - loginStartTime >= loginDatas["expires_in"]:
            print("二维码已过期")
            return login()
        
        intervalDatas = requests.post(f"https://api.tomato-aoarasi.com/phi-login/token/{loginDatas["device_code"]}").json()
        
        if "authData" in intervalDatas:
            print("登录成功")
            return intervalDatas["authData"]
        
        time.sleep(loginDatas["interval"])
    
print(login())