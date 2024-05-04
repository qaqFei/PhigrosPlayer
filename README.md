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
- ```Note```无法在判定线旋转时贴图进行旋转
- 谱面中```Hold```无法生成对应的贴图
- 判定线有严重的锯齿问题

## 命令行参数
- ```-hideconsole``` 隐藏控制台
- ```-clear``` 让程序在清理临时目录完成后退出
- ```-debug``` 显示定位点
- ```-combotips <text>``` 设置连击下的提示 默认为```Autoplay```
- ```-fps <python-eval>``` 设置帧率 默认为```120``` tips:可以使用```-fps "float('inf')"```解除帧率限制
- ```-showfps``` 在标题栏显示帧率
- ```-loop``` 循环播放
- ```-fullscreen``` 全屏
- ```-hidemouse``` 隐藏鼠标
- ```-nofcapline``` 去除```FC/AP```指示器 默认开启```FC/AP```指示器
- ```-noclickeffect``` 关闭点击特效
- ```-holdbody``` 显示```hold```的中间部分

## 编写时的一些坑
- ```tkinter.Canvas``` 的 ```create_line``` 方法 的 ```smooth``` 参数不生效 T_T
- 为 ```note``` 的点击特效增加随机的 正方形扩散时的问题:
    - 资源加载时间增加十几秒
    - 渲染性能跟不上
- 在为 ```note``` 渲染添加缓存后 发现效率更慢了...
- 尝试使用 ```PIL.ImageTk.PhotoImage``` 为判定线 添加抗锯齿 (使用```PIL.ImageDraw```来绘制线条 再用 ```PIL.Image.Image.resize``` 方法添加抗锯齿) 时 发现:
    - 效率实在不行
    - 渲染不完整就下一帧了 而且无法知道是否渲染完整 所以只能增加图片大小 将原图片放在中间 然后进行渲染  后果: 效率更不行了!!!
- 尝试使用 ```PIL.Image.Image.rotate``` 旋转 ```note``` 时 发现:
    - 效率实在不行
    - 锯齿明显

## 声明
- 此项目仅用于学习交流，请勿用于商业用途
- 如有侵权 请联系删除: qaq_fei@163.com 或直接提issue

###### 吐槽一句 tkinter.Canvas 效率感人