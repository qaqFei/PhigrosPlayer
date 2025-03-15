# PhigrosPlayer

![License](https://img.shields.io/badge/license-MIT-yellow)
![Language](https://img.shields.io/badge/language-python-brightgreen)

## 简单的部分功能介绍

- `main.py`: 谱面模拟器
- `tool-rpe2phi.py`: rpe格式谱面转phi格式
- `tool-phi2rpe.py`: phi格式谱面转rpe格式
- `tool-unpack.py`: 自动解包 Phigros 游戏资源, 目前最新支持版本 `3.11.0 (122)`
- `tool-modpack.py`: 自动改包 Phigros （rpe谱面也可以！！
- `tool-dump-global-metadata.py`: 通过 `libUnityPlugin.so` 和 `game.dat` 生成 `global-metadata.dat`
- `tool-fv22fv3`: 将 `formatVersion 2` 谱面转换为 `formatVersion 3`
- `tool-fv32fv2`: 将 `formatVersion 3` 谱面转换为 `formatVersion 2`
- `tool-getPgrUrl.py`: 通过 `taptap API` 获取 Phigros 下载直链
- `phigros.py`: 还原Phigros游戏界面, （真的！

## 环境配置

- Python 版本: `3.12.8`
- Windows

```batch
git clone https://github.com/qaqFei/PhigrosPlayer
cd PhigrosPlayer\src
pip install -r requirements.txt
python main.py <chart> [args] [kwargs]
```

- Termux (运行 `main.py` 后访问 `https://qaqfei.github.io/PhigrosPlayer/src/web_canvas.html` 并触发 `touchstart` 连接 `127.0.0.1` 即可)

```bash
curl https://qaqfei.github.io/PhigrosPlayer/src/termux_install.sh -o install.sh
chmod 777 install.sh
./install.sh

cd PhigrosPlayer/src
python main.py <chart> --disengage-webview [args] [kwargs]
```

## 使用 `phigros.py`

```batch
cd src
python tool-unpack.py <apk> --need-other-illu --need-other-res
python tool-make-pgrassets-byunpack.py .\unpack-result .\phigros_assets

python phigros.py
```

## 谱面兼容

- [x] phi
  - [x] formatVersion
    - [x] 1
    - [x] 2
    - [x] 3
  - [x] offset
  - [x] judgeLineList
    - [x] bpm
    - [x] notesAbove
    - [x] notesBelow
    - [x] speedEvents
    - [x] judgeLineMoveEvents
    - [x] judgeLineRotateEvents
    - [x] judgeLineDisappearEvents
- [ ] rpe
  - [x] BPMList
  - [ ] META (无法获取info文件时读取)
    - [x] RPEVersion (???, 参见 RPEVersion 特殊处理)
    - [x] background
    - [x] charter
    - [x] composer
    - [ ] id
    - [x] level
    - [x] name
    - [x] offset
    - [x] song
  - [ ] judgeLineList
    - [x] Texture
    - [x] bpmfactor
    - [x] father
    - [x] isCover
    - [x] isGif
    - [x] eventLayers
      - [ ] gifEvents (???)
      - [x] alphaEvents
      - [x] moveXEvents
      - [x] moveYEvents
      - [x] rotateEvents
      - [x] speedEvents
    - [ ] extended
      - [x] colorEvents
      - [ ] inclineEvents (???)
      - [x] scaleXEvents
      - [x] scaleYEvents
      - [ ] paintEvents (???)
      - [x] textEvents
    - [x] notes
      - [x] startTime
      - [x] endTime
      - [x] above
      - [x] alpha
      - [x] isFake
      - [x] positionX
      - [x] size
      - [x] speed
      - [x] type
      - [x] visibleTime
      - [x] yOffset
      - [x] hitsound
    - [x] alphaControl (可能有bug)
    - [x] posControl (可能有bug)
    - [x] sizeControl (可能有bug)
    - [ ] skewControl (???)
    - [x] yControl (可能有bug)
    - [x] zOrder
- [x] pec
  - [x] 读取转换为 `rpe` 格式
- [ ] phira resource pack
  - [x] click.png
  - [x] click_mh.png
  - [x] drag.png
  - [x] drag_mh.png
  - [x] hold.png
  - [x] hold_mh.png
  - [x] flick.png
  - [x] flick_mh.png
  - [x] hit_fx.png
  - [x] click.ogg
  - [x] drag.ogg
  - [x] flick.ogg
  - [ ] ending.mp3
  - [ ] info.yml
    - [x] name
    - [x] author
    - [x] description
    - [x] hitFx
    - [x] holdAtlas
    - [x] holdAtlasMH
    - [x] hitFxDuration
    - [x] hitFxScale
    - [x] hitFxRotate
    - [x] hitFxTinted
    - [x] hideParticles
    - [x] holdKeepHead
    - [ ] holdRepeat
    - [x] holdCompact
    - [x] colorPerfect
    - [x] colorGood

### RPEVersion 特殊处理

- `>= 150` 时, `textEvents` 中的 `\n` 才生效, 否则使用 `webview` 默认行为

## 声明

- 此项目仅用于学习交流, 请勿用于商业用途

### 鸣谢

- [7z](https://github.com/ip7z/7zip)
- [openh264](https://github.com/cisco/openh264)
- [libogg](https://github.com/gcp/libogg)
- [libvorbis](https://github.com/xiph/vorbis)
- [oggvorbis2fsb5](https://github.com/uyjulian/oggvorbis2fsb5)
