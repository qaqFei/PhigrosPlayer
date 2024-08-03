# 这是一个使用WebView实现的Phigros谱面的模拟器

## 环境配置
- Python 版本: `3.12.0`
- Windows 版本需 >= `8.1`, `release` 也一样
- 第三方库: [requirements.txt](./requirements.txt)

## 兼容性
- 目前支持`phi`和`rpe`  暂不支持旧`pec`

## 命令行参数
- `--hideconsole` 隐藏控制台
- `--debug` 显示WebView调试工具, 并显示判定线定位点
- `--combotips <string-value>` 设置连击下的提示 默认为`Autoplay`
- `--fullscreen` 全屏
- `--hidemouse` 隐藏鼠标
- `--judgeline-notransparent` 让判定线的`Disappear`始终为`1.0` 也就是说不存在透明度
- `--noclickeffect-randomblock` 禁用打击效果的随机扩散方块
- `--loop` 循环播放
- `--random-block-num <integer-value>` 设置打击效果的随机扩散方块数量 默认为4
- `--scale-note <number-value>` 缩放`Note`
- `--lfdaot` 提前加载帧数据 / Load frame data ahead of time |tips: `--lfdaot`默认会生成.lfdaot文件 可供`--lfdaot-file`使用
- `--lfdaot-file <path-string-value>` 在 `--lfdaot` 的基础上, 不计算谱面数据 而是使用传入的文件数据
- `--size <integer-value> <integer-value>` 指定窗口大小
- `--noclicksound` 禁用打击音效
- `--lfdaot-frame-speed <integer-value>` 设置在使用 `--lfdaot` 时生成 `.lfdaot` 文件的帧率 tip: 在使用 `--lfdaot-file` 时无效
- `--render-range-more` 扩展渲染范围 // 注定仅对Phi谱面生效
- `--render-range-more-scale <number-value>` 扩展渲染范围的缩放 默认为2.0
- `--lfdaot-render-video` 在在使用 `--lfdaot` 和 `--lfdaot-file` 时导出一个视频 视频路径会在加载完成 `.lfdaot` 文件时 弹出文件选择框时确定(也可使用`--lfdaot-render-video-savefp`)
- `--ease-event-interpolation` 在事件插值时使用缓动 tip: 适用于几乎不存在缓动的谱面 否则可能会出现在细小的线性事件中进行缓动插值 从而导致判定线出现移动或旋转卡顿 // 注定仅对Phi谱面生效
- `--frameless` 窗口无边框
- `--window-host <integer-hwnd-value>` 将窗口设置为指定窗口的子窗口
- `--no-mixer-reset-chart-time` 在 `mixer` 的时间与谱面播放时间存在较大误差时 不进行纠正
- `--noautoplay` 禁用`Autoplay`, 进行游玩谱面(目前仅支持键盘操作(a ~ z 26个字母才判定点击, 忽略大小写), 不支持鼠标)
- `--rtacc` 实时`Acc`显示
- `--lfdaot-file-savefp <filepath-string-value>` 在使用`--lfdaot`时`lfdaot`文件的保存路径
- `--lfdaot-render-video-savefp <filepath-string-value>` 在使用`--lfdaot-render-video`的视频保存路径
- `--lfdaot-file-output-autoexit` 在使用`--lfdaot`时 生成`lfdaot`文件后不播放 自动退出

# 快捷键
- 播放中使用长按`Ctrl + Alt + R`可重新开始 (使用`--lfdaot`时失效)

### 声明
- 此项目仅用于学习交流，请勿用于商业用途
- 如有侵权 请联系删除: qaq_fei@163.com 或直接提issue