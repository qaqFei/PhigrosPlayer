# 这是一个使用Tkinter实现的Phigros谱面的模拟器

## 安装依赖
```
pip install -r requirements.txt
```

## 运行
```
python Main.py
```

## 兼容性
- 目前只有Phigros的官谱 且只支持```formatVerison```为```1```或```3```的谱面
- 目前只能读取谱面中的```info.csv```

## 已知问题
- 有概率在启动时窗口无响应
- ~~```Note```无法在判定线旋转时贴图进行旋转~~ <big><big><big><big>已解决</big></big></big></big>
- 谱面中```Hold```无法生成对应的贴图
- 判定线有严重的锯齿问题

## 命令行参数
- ```-hideconsole``` 隐藏控制台
- ```-clear``` 让程序在清理临时目录完成后退出
- ```-debug``` 显示定位点
- ```-combotips <text>``` 设置连击下的提示 默认为```Autoplay```
- ```-fps <python-eval>``` 设置帧率 默认为```120``` tip:可以使用```-fps Const.INF```解除帧率限制
- ```-showfps``` 在标题栏显示帧率
- ```-loop``` 循环播放
- ```-fullscreen``` 全屏
- ```-hidemouse``` 隐藏鼠标
- ```-nofcapline``` 去除```FC/AP```指示器 默认开启```FC/AP```指示器
- ```-noclickeffect``` 关闭点击特效
- ```-holdbody``` 显示```hold```的中间部分
- ```-nojudgeline``` 不显示判定线
- ```-debug-noshow-transparent-judgeline``` 在使用 ```-debug``` 时: 不显示透明度为```0```的判定线
- ```-judgeline-notransparent``` 让判定线的```Disappear```始终为```1.0``` 也就是说不存在透明度

## 声明
- 此项目仅用于学习交流，请勿用于商业用途
- 如有侵权 请联系删除: qaq_fei@163.com 或直接提issue

###### 吐槽一句 tkinter.Canvas 效率感人