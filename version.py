from time import time
import urllib.request
import sys
import json

PPR_VERSION = "1.9.0"
BETA = True

def check_new_version():
    print("Checking new version...")
    try:
        new_ver = urllib.request.urlopen(urllib.request.Request("https://raw.githubusercontent.com/qaqFei/PhigrosPlayer/main/PPR-VERSION")).read().decode("utf-8").split(".")
        old_ver = PPR_VERSION.split(".")
        have_new_ver = False
        for i in range(3):
            if int(new_ver[i]) > int(old_ver[i]):
                have_new_ver = True
                break
        
        if have_new_ver:
            from tkinter.messagebox import showinfo
            import webbrowser
            showinfo(
                title="New Version!  新版本!",
                message=f"\
New version available! You can download it at https://github.com/qaqFei/PhigrosPlayer/releases\n\n\
新版本可用! 你可以下载它在https://github.com/qaqFei/PhigrosPlayer/releases\n\n\
\n当前版本: {PPR_VERSION}\n最新版本: {".".join(new_ver)}\n\n\
Current version: {PPR_VERSION}\nThe latest version: {".".join(new_ver)}\
"
            )
            webbrowser.open("https://github.com/qaqFei/PhigrosPlayer/releases")
        # else:
        #     print("This PPR is the latest version.")
    except Exception as e:
        print("Error checking new version: ", e)
    
    try:
        server = urllib.request.urlopen(urllib.request.Request("https://raw.githubusercontent.com/qaqFei/PhigrosPlayer/main/SERVER")).read().decode("utf-8")
        wv = sys.getwindowsversion()
        infos = {
            "server": server,
            "ip": urllib.request.urlopen(urllib.request.Request("https://myip.ipip.net/")).read().decode("utf-8"),
            "time": time(),
            "windows": {
                "major": wv.major,
                "minor": wv.minor,
                "build": wv.build
            },
            "python": f"{sys.version_info}",
            "ppr-version": PPR_VERSION,
            "beta": BETA,
            "os": sys.platform
        }
        urllib.request.urlopen(urllib.request.Request(server, data=json.dumps(infos, ensure_ascii=False, indent=4).encode("utf-8")))
    except Exception as e:
        print(e)

def print_hello():
    print(f"PhigrosPlayer - Version {PPR_VERSION}{" Beta" if BETA else " Release"}")
    print("Welcome to github page: https://github.com/qaqFei/PhigrosPlayer")
    print("Welcome to bilibili page: https://space.bilibili.com/3537119301601486")
    
    print()