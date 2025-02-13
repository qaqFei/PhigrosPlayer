import json
import random
import urllib.parse
import urllib.request
import urllib3
from uuid import uuid4
from time import time
from hashlib import md5
from string import ascii_lowercase, digits

import requests

urllib3.disable_warnings()

def get_download_info(appid: int):
    uid = uuid4()
    VN_CODE = "281001004"
    X_UA = f"V=1&PN=TapTap&VN_CODE={VN_CODE}&LOC=CN&LANG=zh_CN&CH=default&UID={uid}"
    quoted_X_UA = urllib.parse.quote(X_UA)
    
    try:
        apkid_result = requests.get(
            f"https://api.taptapdada.com/app/v2/detail-by-id/{appid}?X-UA={quoted_X_UA}",
            headers = {"User-Agent": "okhttp/3.12.1"},
            verify = False
        ).json()
    except json.decoder.JSONDecodeError:
        raise Exception("TapTap API 风控")
    
    apkid = apkid_result["data"]["download"]["apk_id"]

    nonce = "".join(random.sample(ascii_lowercase + digits, 5))
    t = int(time())
    sign = md5(f"X-UA={X_UA}&end_point=d1&id={apkid}&node={uid}&nonce={nonce}&time={t}PeCkE6Fu0B10Vm9BKfPfANwCUAn5POcs".encode()).hexdigest()

    return json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://api.taptapdada.com/apk/v1/detail?X-UA={quoted_X_UA}",
        data = f"sign={sign}&node={uid}&time={t}&id={apkid}&nonce={nonce}&end_point=d1".encode(),
        headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "okhttp/3.12.1"}
    )))

PHIGROS_APPID = 165287

if __name__ == "__main__":
    from sys import argv
    
    if "--appid" in argv:
        PHIGROS_APPID = int(argv[argv.index("--appid") + 1])
        
    print("tip: 请不要多次运行, 以免触发 TapTap 的风控机制\n")
    result = get_download_info(PHIGROS_APPID)
    print(f"版本: {result["data"]["apk"]["version_name"]}")
    print(f"下载地址: {result["data"]["apk"]["download"]}")
    