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
1. 目前只有Phigros的官谱 且只支持```formatVerison```为```1```或```3```的谱面
2. 目前只能读取谱面中的```info.csv```

## 已知问题
1. 有概率在启动时窗口无响应
2. ```Note```无法在判定线旋转时贴图进行旋转
3. 谱面中```Hold```无法生成对应的贴图
4. 判定线有严重的锯齿问题

## 命令行参数
1. ```-hideconsole``` 隐藏控制台
2. ```-clear``` 让程序在清理临时目录完成后退出
3. ```-debug``` 显示定位点
4. ```-combotips <text>``` 设置连击下的提示 默认为```Autoplay```
5. ```-noclickeffect``` 禁用点击效果
6. ```-fps <python-eval>``` 设置帧率 默认为```120``` tips:可以使用```-fps "float('inf')"```解除帧率限制
7. ```-showfps``` 在标题栏显示帧率
8. ```-loop``` 循环播放
9. ```-fullscreen``` 全屏
10. ```-hidemouse``` 隐藏鼠标
11. ```-nofcapline``` 去除```FC/AP```指示器 默认开启```FC/AP```指示器

## 声明
1. 此项目仅用于学习交流，请勿用于商业用途
2. 如有侵权 请联系删除: qaq_fei@163.com 或直接提issue

###### 吐槽一句 tkinter.Canvas 效率感人