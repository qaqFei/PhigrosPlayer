# 这里是 Phigros 谱面格式文档

## 前言

尽量详细, 不产生歧义 ヾ(≧▽≦*)o
本文档所使用的类型标注使用 `python` 语法。

目前已知的谱面文档格式有以下:

- Phigros 官方谱面, `json` 格式, 下文简称 `phi` 格式。
- PhiEdit Chart, 命令型文本格式, 下文简称 `pec` 格式。
- Re:PhiEdit 谱面, `json` 格式, 下文简称 `rpe` 格式。
- Phira Bin Chart, 二进制格式, 下文简称 `pbc` 格式。

## Phigros 官方谱面

`phi` 格式谱面为 `json` 格式, 可通过拆包或一些特殊手段获得。

谱面根结构:

- `formatVersion`

    `int` 类型, 值通常为 `typing.Literal[1, 2, 3]`, 表示谱面版本。

- `offset`

    `float` 类型, 表示谱面延迟, 渲染谱面的当前时间时间减去这个值。

    例如需要渲染 `1.0s` 时刻的谱面, `offset` 为 `0.5`, 则当前时间应为 `0.5s`。

- `numOfNotes`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在，在较早时期的 `3` 也存在。
    表示谱面总 `note` 数。

- `judgeLineList`

    `list[dict]` 类型, 表示判定线列表。

`judgeLineList` 的元素结构:

- `numOfNotes`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在，在较早时期的 `3` 也存在。
    表示线总 `note` 数。

- `numOfNotesAbove`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在，在较早时期的 `3` 也存在。
    表示线上方总 `note` 数。

- `numOfNotesBelow`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在，在较早时期的 `3` 也存在。
    表示线下方总 `note` 数。

- `bpm`

    `float` 类型, 表示该线 `bpm` 值。

- `speedEvents`

    `list[dict]` 类型, 表示该线速度事件列表。

- `notesAbove`

    `list[dict]` 类型, 表示线上方 `note` 列表。

- `notesBelow`

    `list[dict]` 类型, 表示线下方 `note` 列表。

- `judgeLineDisappearEvents`

    `list[dict]` 类型, 表示判定线透明度事件列表。

- `judgeLineMoveEvents`

    `list[dict]` 类型, 表示判定线移动事件列表。

- `judgeLineRotateEvents`

    `list[dict]` 类型, 表示判定线旋转事件列表。

我们在此定义时间单位 `T = 1.875 / bpm`, 其中 `bpm` 值为当前线的 `bpm` 值。

我们在此定义大小单位 `W` 与 `H`, 为屏幕的宽度与高度。

我们在此定义大小单位 `X = 0.05625 * W` 与 `Y = 0.6 * H`

`notesAbove` 与 `notesBelow` 的元素结构:

- `type`

    `int` 类型，表示 `note` 类型。
    有以下值:

  - `1` 表示 `tap`。
  - `2` 表示 `drag`。
  - `3` 表示 `hold`。
  - `4` 表示 `flick`。

- `time`

    `int` 类型, 表示 `note` 打击时的时间, 单位为 `T`。

- `positionX`

    `float` 类型, 表示 `note` 横坐标, 单位为 `X`。

    例如值为 `2` 时且判定线无旋转无移动, 打击时在判定线上相对与屏幕左上角的横坐标为 `W / 2 + positionX * X`。

- `holdTime`

    `int` 类型, 表示 `hold` 类型 `note` 的持续时间, 单位为 `T`。
    为 `0` 时不渲染此 `note`。

- `speed`

    `float` 类型, 表示 `note` 的速度,。

  - 对于非 `hold` 类型 `note`, 可直接乘上相对于判定线的纵坐标，无单位。
  - 对于 `hold` 类型 `note`, 在打击前相对于判定线的纵坐标无法通过该键改变，该值表示打击时的速度，单位为 `Y/s`。

- `floorPosition`

    `float` 类型, 在谱面时间为 `0` (包含 `offset`) 时 `note` 的纵坐标, 单位为 `Y`，仅方便计算。
