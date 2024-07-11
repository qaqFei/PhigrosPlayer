# 对于谱面的一些扩展

## `--QFPPR-Note-Width` (已实现)
- 位于 谱面文件的`notesAbove`或`notesBelow`的元素中
- 类型为`int|float`
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

## `--QFPPR-Note-Alpha` (已实现)
- 位于 谱面文件的`notesAbove`或`notesBelow`的元素中
- 类型为`int|float`
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

## `--QFPPR-JudgeLine-TextJudgeLine` (已实现)
- 位于 谱面文件的`judgeLineList`的元素中
- 类型为`bool`
- 用于标注是否应用`--QFPPR-JudgeLine-TextEvents`
- 若为`true`, 则判定线永远为文字, 默认为`false`

## `--QFPPR-JudgeLine-TextEvents` (已实现)
- 位于 谱面文件的`judgeLineList`的元素中
- 类型为`list`
- 需要`--QFPPR-JudgeLine-TextJudgeLine`为`true`时才有意义
- 无符合的事件, 则为`""`(空字符串)
- 事件的 `startTime` 应不重复
- 示例:
    ```json
    {
        "bpm": 140.0,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [{"startTime": 0.0, "endTime": 1000000000.0, "value": 1.0}],
        "judgeLineMoveEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 0.5, "end": 0.5, "start2": 0.2, "end2": 0.2}],
        "judgeLineRotateEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 0.0, "end": 0.0}],
        "judgeLineDisappearEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 1.0, "end": 1.0}],
        "--QFPPR-JudgeLine-TextJudgeLine": true,
        "--QFPPR-JudgeLine-TextEvents": [
            {
                "startTime": 128.0,
                "value": "Hello World!"
            },
            {
                "startTime": 512.0,
                "value": "Hello World at 1.875 / 140 * 512 sec!"
            }
        ]
    }
    ```

## `--QFPPR-Note-Fake` (已实现)
- 位于 谱面文件的`notesAbove`或`notesBelow`的元素中
- 类型为`bool`
- 为`true`时, `note`只会被渲染, 不做其他处理, 不参加总分的计算
- 示例:
    ```json
    {
        "type": 1,
        "time": 128.0,
        "holdTime": 0.0,
        "floorPosition": 2.742857142857143,
        "speed": 1.0,
        "--QFPPR-Note-Fake": true
    }
    ```

## `--QFPPR-Note-VisibleTime` (已实现)
- 位于 谱面文件的`notesAbove`或`notesBelow`的元素中
- 类型为`int|float`
- 距离打击...秒时, 才显示`note`
- 示例:
    ```json
    {
        "type": 1,
        "time": 128.0,
        "holdTime": 0.0,
        "floorPosition": 2.742857142857143,
        "speed": 1.0,
        "--QFPPR-Note-VisibleTime": 0.25
    }
    ```

## `--QFPPR-Extra-Enable`
- 位于 谱面文件的`/`
- 类型为`bool`, 默认为`false`
- 只有为`true`时, `--QFPPR-Extra`才生效

## `--QFPPR-Extra`
- 位于 谱面文件的`/`
- 类型为`int|float`
- 类似`rpe`中的`extra.json`

## `--QFPPR-JudgeLine-EnableTexture` (已实现)
- 位于 谱面文件的`judgeLineList`的元素中
- 类型为`bool`, 默认为`false`
- 只有为`true`时, `--QFPPR-JudgeLine-Texture`才生效

## `--QFPPR-JudgeLine-Texture` (已实现)
- 位于 谱面文件的`judgeLineList`的元素中
- 类型为`str`, 为图片的`base64`编码

## `--QFPPR-JudgeLine-ScaleXEvents` & `--QFPPR-JudgeLine-ScaleYEvents` (已实现)
- 位于 谱面文件的`judgeLineList`的元素中
- 类型为`list`
- 示例:
    ```json
    {
        "bpm": 140.0,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [{"startTime": 0.0, "endTime": 1000000000.0, "value": 1.0}],
        "judgeLineMoveEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 0.5, "end": 0.5, "start2": 0.2, "end2": 0.2}],
        "judgeLineRotateEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 0.0, "end": 0.0}],
        "judgeLineDisappearEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 1.0, "end": 1.0}],
        "--QFPPR-JudgeLine-EnableTexture": true,
        "--QFPPR-JudgeLine-Texture": "Texture Base64 Data",
        "--QFPPR-JudgeLine-ScaleXEvents": [
            {
                "startTime": -999999.0,
                "endTime": 0.0,
                "start": 0.1,
                "end": 0.1,
                "easingType": 1
            },
            {
                "startTime": 0.0,
                "endTime": 128.0,
                "start": 1.0,
                "end": 0.3,
                "easingType": 2
            },
            {
                "startTime": 128.0,
                "endTime": 1000000000.0,
                "start": 1.0,
                "end": 1.0,
                "easingType": 1
            },
        ]
    }

## `--QFPPR-JudgeLine-ColorEvents` (已实现)
- 位于 谱面文件的`judgeLineList`的元素中
- 类型为`list`
- 示例:
    ```json
    {
        "bpm": 140.0,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [{"startTime": 0.0, "endTime": 1000000000.0, "value": 1.0}],
        "judgeLineMoveEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 0.5, "end": 0.5, "start2": 0.2, "end2": 0.2}],
        "judgeLineRotateEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 0.0, "end": 0.0}],
        "judgeLineDisappearEvents": [{"startTime": -999999.0, "endTime": 1000000000.0, "start": 1.0, "end": 1.0}],
        "--QFPPR-JudgeLine-ColorEvents": [
            {
                "startTime": -999999.0,
                "value": [255, 255, 255],
            },
            {
                "startTime": 0.0,
                "value": [114, 51, 4]
            },
            {
                "startTime": 128.0,
                "value": [0, 0, 0]
            },
        ]
    }