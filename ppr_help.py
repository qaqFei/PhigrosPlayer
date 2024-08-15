HELP_EN = '''\
Usage: Main <chart_file> [<args>...] [<kwargs>...]

<Args>
  --hideconsole: Hide the console window.
  --debug: Display webview debug window, and show judgeLine position points.
  --fullscreen: Make the window fullscreen.
  --judgeline-notransparent: Make the judgeLine not transparent. (Disappear value forever is 1.0.)
  --noclickeffect-randomblock: Disable random block of click effect.
  --loop: Auto loop the chart.
  --lfdaot: Load frame data ahead of time, and output a *.lfdaot file.
  --noclicksound: Disable click sound.
  --render-range-more: Render range more, can render out of the screen, and display at screen.
  --lfdaot-render-video: Output a video file when using --lfdaot and --lfdaot-file.
  --frameless: Make the window frameless.
  --no-mixer-reset-chart-time: If there is a large discrepancy between the mixer's time and the chart's playback time, it will not be corrected.
  --noautoplay: Disable auto play.
  --rtacc: Enable real-time accuracy.
  --lfdaot-file-output-autoexit: when using --lfdaot and saved lfdaot file, noplay, and auto exit. (Front-loaded arg: --lfdaot)
  --lowquality: Use low quality render.
  --showfps: Show fps. when using --lfdaot-render-video, it will not be displayed.
  --noplaychart: Do not play the chart, immediately settle.

<Kwargs>
  --combotips <string-value>: Set the combo tips text.
  --random-block-num <integer-value>: Set the random block of click effect number.
  --scale-note <number-value>: Set the note scale.
  --lfdaot-file <filepath-string-value>: Set the *.lfdaot file path, and load it and play it. (Front-loaded arg: --lfdaot)
  --size <integer-value> <integer-value>: Set the window size.
  --lfdaot-frame-speed <integer-value>: Set the frame speed of *.lfdaot file. (Front-loaded arg: --lfdaot, Invalid when using --lfdaot-file)
  --render-range-more-scale <number-value>: Set the render range more scale. (Front-loaded arg: --render-range-more)
  --window-host <integer-hwnd-value>: Set the window host hwnd.
  --lfdaot-file-savefp <filepath-string-value>: when using --lfdaot, set the lfdaot file save path. (Front-loaded arg: --lfdaot)
  --lfdaot-render-video-savefp <filepath-string-value>: when using --lfdaot and --lfdaot-render-video, set the video file save path. (Front-loaded arg: --lfdaot and --lfdaot-render-video)
  --lowquality-scale <float-value>: Set the low quality render scale. default: 2.0
  --res <res-path>: Set the resource path.
  --lfdaot-start-frame-num <number-value>: Set the start frame number of *.lfdaot file. (Front-loaded arg: --lfdaot, Invalid when using --lfdaot-file) // only use at very big chart file video render.
  --lfdaot-run-frame-num <number-value>: Set the frame number count of *.lfdaot file. (Front-loaded arg: --lfdaot, Invalid when using --lfdaot-file) // only use at very big chart file video render.
  --speed <number-value>: Set the speed.
  --render-begin-loading-animation-video <filepath-string-value>: output a chart start animation video to the path. (fps: 120, noaudio)
  --render-begin-judge-line-animation-video <filepath-string-value>: output a chart start judge line animation video to the path. (fps: 120, noaudio)
  --render-before-finish-animation-video <filepath-string-value>: output a chart UI animation video to the path. (fps: 120, noaudio)
  --render-finish-animation-video <filepath-string-value>: output a chart finish animation video to the path. (fps: 120, noaudio) tip: when video is rendering, buttons will be blocked.
  --clickeffect-randomblock-roundn <number-value>: Set the round number of random block click effect. (0.0 ~ 0.5) (default: 0)
'''

HELP_ZH = '''\
使用: Main <谱面文件> [<参数>...] [<关键字参数>...]

<参数>
  --hideconsole: 隐藏控制台窗口
  --debug: 显示webview调试窗口, 并显示判定线位置点
  --fullscreen: 使窗口全屏
  --judgeline-notransparent: 使判定线不透明
  --loop: 自动循环谱面
  --lfdaot: 提前加载帧数据, 并输出一个 *.lfdaot 文件
  --noclicksound: 禁用点击音效
  --render-range-more: 渲染范围更多, 可以渲染出屏幕外, 并显示在屏幕上
  --lfdaot-render-video: 使用 --lfdaot 和 --lfdaot-file 时输出一个视频文件
  --frameless: 使窗口无边框
  --no-mixer-reset-chart-time: 如果音频的时间和谱面的播放时间有较大的偏差, 不会进行修正
  --noautoplay: 禁用自动播放
  --rtacc: 启用实时准度
  --lfdaot-file-output-autoexit: 使用 --lfdaot 和保存的 lfdaot 文件, 自动退出. (前置参数: --lfdaot)
  --lowquality: 低画质模式
  --showfps: 显示帧率
  --noplaychart: 不播放谱面, 立即结算

<关键字参数>
  --combotips <字符串>: 设置连击提示文本
  --random-block-num <整数>: 设置随机块点击效果数量
  --scale-note <数字>: 设置音符缩放
  --lfdaot-file <文件路径字符串>: 设置 *.lfdaot 文件路径, 并加载并播放它. (前置参数: --lfdaot)
  --size <整数> <整数>: 设置窗口大小
  --lfdaot-frame-speed <整数>: 设置 *.lfdaot 文件的帧速度. (前置参数: --lfdaot, 使用 --lfdaot-file 时无效)
  --render-range-more-scale <数字>: 设置渲染范围更多的缩放. (前置参数: --render-range-more)
  --window-host <整数-窗口句柄>: 设置窗口宿主 窗口句柄
  --lfdaot-file-savefp <文件路径字符串>: 使用 --lfdaot 时, 设置 lfdaot 文件保存路径. (前置参数: --lfdaot)
  --lowquality-scale <浮点数>: 设置低画质渲染缩放 默认: 2.0
  --res <资源路径>: 设置资源路径
  --lfdaot-start-frame-num <数字>: 设置 *.lfdaot 文件的开始帧数 (前置参数: --lfdaot, 使用 --lfdaot-file 时无效) // 仅在非常大的谱面文件视频渲染时使用
  --lfdaot-run-frame-num <数字>: 设置生成 *.lfdaot 文件的目标帧数 (前置参数: --lfdaot, 使用 --lfdaot-file 时无效) // 仅在非常大的谱面文件视频渲染时使用
  --speed <数字>: 设置谱面速度
  --render-begin-loading-animation-video <filepath-string-value>: 导出一个谱面开始的加载动画到指定路径 (帧率恒定120, 无声音)
  --render-begin-judge-line-animation-video <filepath-string-value>: 导出一个谱面开始的判定线展开动画到指定路径 (帧率恒定120, 无声音)
  --render-before-finish-animation-video <filepath-string-value>: 导出一个谱面结束UI过渡动画到指定路径 (帧率恒定120, 无声音)
 --clickeffect-randomblock-roundn <number-value>: 设置打击效果方块的圆角系数 (0.0 = 方, 0.5 = 圆), 默认 = 0.0
'''