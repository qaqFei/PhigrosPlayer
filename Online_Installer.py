from urllib.request import Request, urlopen
from os import startfile

f = open("PPR-Installer.exe", "wb")
installer_url = urlopen(Request("https://raw.githubusercontent.com/qaqFei/PhigrosPlayer/main/LASTEST_VERSION_DOWNLOADPATH")).read().decode("utf-8")
data = urlopen(Request(installer_url)).read()
f.write(data)
f.close()
startfile("PPR-Installer.exe")