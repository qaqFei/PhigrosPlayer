clear

apt update && apt upgrade -y
apt install x11-repo git -y

read -p "请输入git clone的地址喵 (例如 github.com): " git_address
git clone https://$git_address/qaqFei/PhigrosPlayer --depth 1

if [ ! -d ./PhigrosPlayer ]; then
    echo 请检查网络喵~
    exit 1
fi

cd ./PhigrosPlayer/src

apt install python3 -y
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

apt install sdl2 sdl2-mixer xorgproto -y
pip --no-cache-dir install -r requirements_android.txt

apt install ffmpeg p7zip -y

clear
echo Tip: 安装完了喵, 记得使用的时候加上 --disengage-webview 喵 ~
