# 这是一个使用WebView实现的Phigros谱面的模拟器

## 安装依赖
```
pip install -r requirements.txt
```

## 运行
```
python Main.py
```

## 兼容性
- 目前只支持Phigros的官谱 且只支持```formatVersion```为```1```或```3```的谱面 (正在逐步支持 ```Re:PhiEdit``` 谱面  还要好久...)
- 目前只能读取谱面中的```info.csv```

## 已知问题
- 有概率在启动时窗口无响应 (存疑 如出现欢迎提issue)
- 谱面中```Hold```无法生成对应的贴图
- 判定线有严重的锯齿问题 (存疑 如出现欢迎提issue)

## 命令行参数 (大部分 仅对phigros官谱生效)
- ```-hideconsole``` 隐藏控制台
- ```-debug``` 显示WebView调试工具
- ```-combotips <text>``` 设置连击下的提示 默认为```Autoplay```
- ```-showfps``` 在标题栏显示帧率
- ```-fullscreen``` 全屏
- ```-hidemouse``` 隐藏鼠标
- ```-nojudgeline``` 不显示判定线
- ```-judgeline-notransparent``` 让判定线的```Disappear```始终为```1.0``` 也就是说不存在透明度
- ```-noclickeffect-randomblock``` 禁用打击效果的随机扩散方块
- ```-loop``` 循环播放
- ```-random-block-num <value>``` 设置打击效果的随机扩散方块数量 默认为4

## 声明
- 此项目仅用于学习交流，请勿用于商业用途
- 如有侵权 请联系删除: qaq_fei@163.com 或直接提issue