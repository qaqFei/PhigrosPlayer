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
- 无啦!

## 命令行参数 (大部分 仅对phigros官谱生效)
- ```-hideconsole``` 隐藏控制台
- ```-debug``` 显示WebView调试工具
- ```-combotips <string-value>``` 设置连击下的提示 默认为```Autoplay```
- ```-showfps``` 在标题栏显示帧率
- ```-fullscreen``` 全屏
- ```-hidemouse``` 隐藏鼠标
- ```-nojudgeline``` 不显示判定线
- ```-judgeline-notransparent``` 让判定线的```Disappear```始终为```1.0``` 也就是说不存在透明度
- ```-noclickeffect-randomblock``` 禁用打击效果的随机扩散方块
- ```-loop``` 循环播放
- ```-random-block-num <integer-value>``` 设置打击效果的随机扩散方块数量 默认为4
- ```-scale-note <number-value>``` 缩放```Note```
- ```-lfdaot``` 提前加载帧数据 / Load frame data ahead of time |tips: ```-lfdaot```默认会生成.lfdaot文件 可供```-lfdaot-file```使用
- ```-lfdaot-file <path-string-value>``` 在 ```-lfdaot``` 的基础上, 不计算谱面数据 而是使用传入的文件数据
- ```-size <integer-value> <integer-size>``` 指定窗口大小

## 声明
- 此项目仅用于学习交流，请勿用于商业用途
- 如有侵权 请联系删除: qaq_fei@163.com 或直接提issue