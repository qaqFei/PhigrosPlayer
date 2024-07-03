# 对于谱面的一些扩展

## `--QFPPR-Note-Width`
- 位于 谱面文件的`notesAbove`或`notesBelow`的元素中
- 使用示例(将Note宽度设置为原大小的2.0倍):
    ```json
    {
        "type": 1,
        "time": 128.0,
        "holdTime": 0.0,
        "floorPosition": 2.742857142857143,
        "speed": 1.0,
        "--QFPPR-Note-Width": 2.0
    }
    ```

## `--QFPPR-Note-Alpha`
- 位于 谱面文件的`notesAbove`或`notesBelow`的元素中
- 使用示例(将Note透明度设置为40%):
    ```json
    {
        "type": 1,
        "time": 128.0,
        "holdTime": 0.0,
        "floorPosition": 2.742857142857143,
        "speed": 1.0,
        "--QFPPR-Note-Alpha": 0.4
    }
    ```