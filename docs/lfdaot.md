# 关于 ```.lfdaot``` 文件

## 介绍
- 在使用```-lfdaot```启动主程序时 如果不带```-lfdaot-file```参数 那么在计算完成渲染后 会自动生成一个 ```.lfdaot``` 文件

## 文件格式
- 使用```JSON```格式进行存储
- 结构 (示例)
    ```js
    {
        "meta": {
            "frame_speed": 60, // 文件的播放帧率
            "frame_num": 6000, // 文件包含的总帧数 (len(data))
            "render_range_more": false, // 见README.md的参数: -render-range-more
            "render_range_more_scale": 2.0, // 见README.md的参数: -render-range-more-scale
            "size": [1920, 1080] // 文件的分辨率
        },
        "data": [ // 数据 每一帧为一个 object
            {
                "render": [ // 渲染指令列表
                    { // 单个渲染指令
                        "func_name": "create_.../ clear_canvas/ ...", // 渲染函数名
                        "args": [ // 渲染函数的参数
                            232,
                            56,
                            232,
                            57 // ...
                        ],
                        "kwargs": { // 渲染函数的关键字参数
                            "fillStyle": "rgba(255, 255, 255, 0.5)",
                            "...": null //...
                        }
                    } //...
                ],
                "ex": [ // 扩展指令列表
                    ["set", "...", "..."], // 单个指令
                    ["...", "..."] //...
                ]
            } //...
        ]
    }
    ```

- 渲染指令函数名:
    - 位于```project/web_canvas.py``` 中的 ```WebCanvas``` 对象的所有方法
    - 位于```project/Main.py``` 中的 所有函数

- 扩展指令:
    - ```set``` ```<var_name>``` ```<value>``` # 设置变量
    - ```break``` # 跳出循环 结束播放 一般存在于最后一个ex ```(obj["data"][-1]["ex"])```
    - ```thread-call``` ```<any-function-name>``` ```<eval-tuple-args>``` # 使用线程启动函数

## 注意
- ```<any-function-name>``` 位于 ```project/Main.py``` 中的 所有函数
- ```<eval-tuple-args>``` 使用 ```eval(v)``` 得到最终值 类型为```typing.Tuple```