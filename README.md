# 这是一个使用WebView实现的Phigros谱面的模拟器

## 环境配置

- Python 版本: `3.12.7`
- Windows 版本需 >= `8.1`
- 第三方库: [requirements.txt](./src/requirements.txt)

## 谱面兼容

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
    - [ ] RPEVersion (???, 有影响吗?)
    - [x] background
    - [x] charter
    - [x] composer
    - [ ] id
    - [x] level
    - [x] name
    - [x] offset
    - [x] song
  - [x] judgeLineGroup (谱面播放不使用)
  - [ ] judgeLineList
    - [x] Group (谱面播放不使用)
    - [x] Name (谱面播放不使用)
    - [x] Texture
    - [x] bpmfactor (?, 按照字母意思: bpm速率进行处理)
    - [x] father
    - [x] isCover
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
      - [ ] speed (???)
      - [x] type
      - [x] visibleTime
      - [ ] yOffset
    - [x] numOfNotes (未使用)
    - [x] alphaControl (有bug)
    - [x] posControl (有bug)
    - [x] sizeControl (有bug)
    - [ ] skewControl
    - [x] yControl (有bug)
    - [x] zOrder
  - [x] multiLineString (谱面播放不使用)
  - [x] multiScale (谱面播放不使用)
- [x] pec
  - 读取转换为`rpe`格式
- 补充
  - [ ] rpe格式中的事件
    - [ ] bezier
    - [ ] bezierPoints (???)
    - [ ] easingLeft (???)
    - [ ] easingRight (???)
    - [x] easingType
    - [x] start
    - [x] end
    - [x] startTime
    - [x] endTime
    - [ ] linkgroup (???)

</details>

## 声明

- 此项目仅用于学习交流，请勿用于商业用途
