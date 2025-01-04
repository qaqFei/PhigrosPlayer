# 这是一个使用WebView实现的Phigros谱面的模拟器

## 环境配置

- Python 版本: `3.12.8`
- Windows 版本需 >= `8.1`
- 第三方库: [requirements.txt](./src/requirements.txt)

## 谱面兼容

tip: 对于谱面播放不使用的部分, 此处忽略

<details>
<summary>展开</summary>

- [x] phi
  - [x] formatVersion
    - [x] 1
    - [x] 3
    - [x] others
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
    - [x] bpmfactor (?, 按照字母意思: bpm速率进行处理)
    - [x] father
    - [x] isCover
    - [ ] isGif
    - [x] eventLayers
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
    - [ ] skewControl
    - [x] yControl (可能有bug)
    - [x] zOrder
- [x] pec
  - 读取转换为`rpe`格式
- 补充
  - [x] rpe格式中的事件
    - [x] bezier
    - [x] bezierPoints
    - [x] easingLeft
    - [x] easingRight
    - [x] easingType
    - [x] start
    - [x] end
    - [x] startTime
    - [x] endTime

### RPEVersion 特殊处理

- `>= 153` 时, `textEvents` 中的 `\n` 才生效, 否则使用 `webview` 默认行为

</details>

## 网页版的 `PhigrosPlayer` ?

这仅仅为了在其他平台或户外使用的目的, 没有过多的优化, 不常维护

Release: [webphiplayer-release](https://qaqfei.github.io/PhigrosPlayer/src/webphiplayer.html)
Dev: [webphiplayer-dev](https://qaqfei.github.io/PhigrosPlayer/src/webphiplayer_dev.html)

## 声明

- 此项目仅用于学习交流，请勿用于商业用途
