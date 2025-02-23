# 这里是 Phigros 谱面格式文档

## 前言

（没写完

尽量详细, 不产生歧义 ヾ(≧▽≦*)o

本文档所使用的类型标注使用 `python` 语法。

目前已知的谱面格式有以下:

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

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在, 在较早时期的 `3` 也存在。
    表示谱面总 `note` 数。

- `judgeLineList`

    `list[dict]` 类型, 表示判定线列表。

`judgeLineList` 的元素结构:

- `numOfNotes`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在, 在较早时期的 `3` 也存在。
    表示线总 `note` 数。

- `numOfNotesAbove`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在, 在较早时期的 `3` 也存在。
    表示线上方总 `note` 数。

- `numOfNotesBelow`

    `int` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在, 在较早时期的 `3` 也存在。
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

时间单位均为 128 分音符 即 `60 / 32 / bpm`, 下文简写为 `1.875 / bpm`。

我们在此定义时间单位 `T = 1.875 / bpm`, 其中 `bpm` 值为当前线的 `bpm` 值。

我们在此定义大小单位 `W` 与 `H`, 为屏幕的宽度与高度。

我们在此定义大小单位 `X = 0.05625 * W` 与 `Y = 0.6 * H`

`notesAbove` 与 `notesBelow` 的元素结构:

- `type`

    `int` 类型, 表示 `note` 类型。
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

  - 对于非 `hold` 类型 `note`, 可直接乘上相对于判定线的纵坐标, 无单位。
  - 对于 `hold` 类型 `note`, 在打击前相对于判定线的纵坐标无法通过该键改变, 该值表示打击时的速度, 单位为 `Y/s`。

- `floorPosition`

    `float` 类型, 在谱面时间为 `0` (包含 `offset`) 时 `note` 的纵坐标, 单位为 `Y`, 仅方便计算。

`speedEvents` 的元素结构:

- `startTime`

    `int` 类型, 表示速度事件开始时间, 单位为 `T`。
    一般与上一个事件的 `endTime` 相同, 如果为第一个事件则为 `0`。

- `endTime`

    `int` 类型, 表示速度事件结束时间, 单位为 `T`。
    一般与下一个事件的 `startTime` 相同, 如果为最后一个事件则为 `1e9`。

- `value`

    `float` 类型, 表示速度事件的速度, 单位为 `Y/s`。

- `floorPosition`

    `float` 类型, 在 `formatVersion` 为 `1` 或 `2` 时存在, 在较早时期的 `3` 也存在。

    表示事件开始时刻判定线流过的速度, 单位为 `Y/s`, 仅方便计算。

`judgeLineDisappearEvents` 的元素结构:

- `startTime`

    `int` 类型, 表示透明度事件开始时间, 单位为 `T`。
    一般与上一个事件的 `endTime` 相同, 如果为第一个事件则为 `-1e6+1`。

- `endTime`

    `int` 类型, 表示透明度事件结束时间, 单位为 `T`。

    一般与下一个事件的 `startTime` 相同, 如果为最后一个事件则为 `1e9`。

- `start`

    `float` 类型, 表示透明度事件开始透明度。

    一般地, 值为 `0 ~ 1`, 表示不透明度。

- `end`

    `float` 类型, 表示透明度事件结束透明度。

    一般地, 值为 `0 ~ 1`, 表示不透明度。

- `start2` & `end2`

    为 `float` 类型, 在 `formatVersion` 为 `2` 时存在, 在较早时期的 `3` 也存在。

    一般地, 值恒为 `0`。

`judgeLineMoveEvents` 的元素结构:

- `startTime`

    `int` 类型, 表示移动事件开始时间, 单位为 `T`。
    一般与上一个事件的 `endTime` 相同, 如果为第一个事件则为 `-1e6+1`。

- `endTime`

    `int` 类型, 表示移动事件结束时间, 单位为 `T`。
    一般与下一个事件的 `startTime` 相同, 如果为最后一个事件则为 `1e9`。

- `start` & `start2`

    `float` 类型, 表示移动事件开始位置。

    `start` 为 x 坐标, `start2` 为 y 坐标。

- `end` & `end2`

    `float` 类型, 表示移动事件结束位置。

    `end` 为 x 坐标, `end2` 为 y 坐标。

！注意: 坐标原点位于屏幕左下角。

对于 `formatVersion` 为 `1` 的谱面, 不存在 `start2` 与 `end2`。

坐标 x 单位为 `W / 880`, y 单位为 `H / 520`。

此时的坐标计算如下:

```python
def unpack_pos(number: int):
    x, y = (number - number % 1000) // 1000, number % 1000
    return x / 880 * W, y / 520 * H

start_x, start_y = unpack_pos(event.start)
end_x, end_y = unpack_pos(event.end)
```

对于 `formatVersion` 为 `2` 和 `3` 的谱面, 存在 `start2` 与 `end2`, 此时的坐标计算如下:

```python
start_x, start_y = event.start * W, event.start2 * H
end_x, end_y = event.end * W, event.end2 * H
```

`judgeLineRotateEvents` 的元素结构:

- `startTime`

    `int` 类型, 表示旋转事件开始时间, 单位为 `T`。
    一般与上一个事件的 `endTime` 相同, 如果为第一个事件则为 `-1e6+1`。

- `endTime`

    `int` 类型, 表示旋转事件结束时间, 单位为 `T`。
    一般与下一个事件的 `startTime` 相同, 如果为最后一个事件则为 `1e9`。

- `start`

    `float` 类型, 表示旋转事件开始角度。
    单位为 `deg`, 逆时针。

- `end`

    `float` 类型, 表示旋转事件结束角度。
    单位为 `deg`, 逆时针。

至此, 基本的谱面格式已经介绍完毕。

但是！

对于 `formatVersion` 为 `2` 的谱面:

`note` 存在以下键:

- `headSpeed`

    `float` 类型, 在转换为 `formatVersion` 为 `3` 时为 `hold` 类型 `note` 的 `speed` 值。

- `judgeLineIndex`

    `int` 类型, 表示 `note` 所在判定线 `index`。

    不影响渲染。

- `isNotesAbove`

    `bool` 类型, 表示 `note` 是否在 `notesAbove` 之中。

    不影响渲染。

- `needDelet`

    `bool` 类型, 表示 `note` 是否需要删除。

    不影响渲染。

事件存在以下值:

- `easeType`

    `int` 类型, 表示事件缓动类型。

    在下文定义。

- `easeType2`

    `int` 类型, 表示事件缓动类型。

    一般地, 非移动事件此值恒为 `0`, 表示移动事件 y 轴缓动类型。

    在下文定义。

- `useEndNode`

    `bool` 类型, 表示事件是否使用结束节点。

    在转化为 `formatVersion` 为 `3` 时, 如果为 `True`, 则 `end` 或 `end2` 值为当前事件的 `end` 或 `end2` 值, 否则为下一个事件的 `start` 或 `start2` 值。

缓动类型定义:

```python
import math
import typing

ease_funcs: list[typing.Callable[[float], float]] = [
    lambda t: t, # 0 - linear
    lambda t: 1 - math.cos(t * math.pi / 2), # 1 - inSine
    lambda t: math.sin(t * math.pi / 2), # 2 - outSine
    lambda t: (1 - math.cos(t * math.pi)) / 2, # 3 - inOutSine
    lambda t: t ** 2, # 4 - inCubic
    lambda t: 1 - (t - 1) ** 2, # 5 - outCubic
    lambda t: (t ** 2 if (t := t * 2) < 1 else -((t - 2) ** 2 - 2)) / 2, # 6 - inOutCubic
    lambda t: t ** 3, # 7 - inQuint
    lambda t: 1 + (t - 1) ** 3, # 8 - outQuint
    lambda t: (t ** 3 if (t := t * 2) < 1 else (t - 2) ** 3 + 2) / 2, # 9 - inOutQuint
    lambda t: t ** 4, # 10 - inCirc
    lambda t: 1 - (t - 1) ** 4, # 11 - outCirc
    lambda t: (t ** 4 if (t := t * 2) < 1 else -((t - 2) ** 4 - 2)) / 2, # 12 - inOutCirc
    lambda _: 0, # 13 - zero
    lambda _: 1 # 14 - one
]
```

<details>
  <summary>你知道的太多了。</summary>

  为确保 `formatVersion` 为 `2` 的谱面转化为 `formatVersion` 为 `3` 的谱面的准确性和文档的严谨性 (此处为早期 `formatVersion 3` 谱面, 版本为 `v2.5.0` 以前):

  ```C#
  using System;
  using System.Collections;
  using System.Collections.Generic;
  using System.IO;
  using System.Runtime.InteropServices;
  using SaveSystem;
  using TMPro;
  using UnityEngine;
  using UnityEngine.Networking;
  using UnityEngine.SceneManagement;
  using UnityEngine.UI;
  
  public class SpeedEvent
  {
      public float startTime;
      public float endTime;
      public float floorPosition;
      public float value = 1f;
  }
  
  public class ChartNote
  {
      public int type;
      public int time;
      public float positionX;
      public float holdTime;
      public float speed;
      public float floorPosition;
      public float headSpeed;
      public int judgeLineIndex;
      public bool isNotesAbove = true;
      public bool needDelet;
  }
  
  public class JudgeLine
  {
      public int numOfNotes;
      public int numOfNotesAbove;
      public int numOfNotesBelow;
      public float bpm;
  
      public List<SpeedEvent> speedEvents;
      public List<ChartNote> notesAbove;
      public List<ChartNote> notesBelow;
      public List<JudgeLineEvent> judgeLineDisappearEvents;
      public List<JudgeLineEvent> judgeLineMoveEvents;
      public List<JudgeLineEvent> judgeLineRotateEvents;
  }
  
  public class JudgeLineEvent
  {
      public float startTime;
      public float endTime;
      public float start;
      public float end;
      public float start2;
      public float end2;
      public int easeType;
      public int easeType2;
      public bool useEndNode;
  }
  
  public class Chart
  {
      public int formatVersion;
      public float offset;
      public int numOfNotes;
  
      public List<JudgeLine> judgeLineList;
  }
  
  public class CompatibilitySpeedEvent
  {
      public float startTime;
      public float endTime;
      public float floorPosition;
      public float value;
  }
  
  public class CompatibilityChartNote
  {
      public int type;
      public int time;
      public float positionX;
      public float holdTime;
      public float speed;
      public float floorPosition;
  }
  
  public class CompatibilityJudgeLineEvent
  {
      public float startTime;
      public float endTime;
      public float start;
      public float end;
      public float start2;
      public float end2;
  }
  
  public class CompatibilityJudgeLine
  {
      public int numOfNotes;
      public int numOfNotesAbove;
      public int numOfNotesBelow;
      public float bpm;
  
      public List<CompatibilitySpeedEvent> speedEvents;
      public List<CompatibilityChartNote> notesAbove;
      public List<CompatibilityChartNote> notesBelow;
      public List<CompatibilityJudgeLineEvent> judgeLineDisappearEvents;
      public List<CompatibilityJudgeLineEvent> judgeLineMoveEvents;
      public List<CompatibilityJudgeLineEvent> judgeLineRotateEvents;
  }
  
  public class CompatibilityChart
  {
      public int formatVersion;
      public float offset;
      public int numOfNotes;
  
      public List<CompatibilityJudgeLine> judgeLineList;
  }
  
  namespace ProjectHub
  {
      public class EditProject : MonoBehaviour
      {
          public void SaveAsNewFormat()
          {
              string str = "";
              for (int i = 0; i < 4; i++)
              {
                  if (this.projectFile.ifChartloaded[i])
                  {
                      switch (i)
                      {
                      case 0:
                          str = "/Chart_EZ.json";
                          break;
                      case 1:
                          str = "/Chart_HD.json";
                          break;
                      case 2:
                          str = "/Chart_IN.json";
                          break;
                      case 3:
                          str = "/Chart_AT.json";
                          break;
                      }
                      Chart chart = JsonUtility.FromJson<Chart>(File.ReadAllText(this.chartFilePath + str));
                      CompatibilityChart compatibilityChart = new CompatibilityChart();
                      compatibilityChart.formatVersion = 3;
                      compatibilityChart.offset = chart.offset;
                      compatibilityChart.numOfNotes = chart.numOfNotes;
                      compatibilityChart.judgeLineList = new List<CompatibilityJudgeLine>();
                      int num = 0;
                      while (num < 24 && num < chart.judgeLineList.Count)
                      {
                          CompatibilityJudgeLine compatibilityJudgeLine = new CompatibilityJudgeLine();
                          compatibilityJudgeLine.bpm = chart.judgeLineList[num].bpm;
                          compatibilityJudgeLine.numOfNotes = chart.judgeLineList[num].numOfNotes;
                          compatibilityJudgeLine.numOfNotesAbove = chart.judgeLineList[num].numOfNotesAbove;
                          compatibilityJudgeLine.numOfNotesBelow = chart.judgeLineList[num].numOfNotesBelow;
                          compatibilityJudgeLine.notesAbove = new List<CompatibilityChartNote>();
                          if (chart.judgeLineList[num].notesAbove.Count > 0)
                          {
                              foreach (ChartNote chartNote in chart.judgeLineList[num].notesAbove)
                              {
                                  CompatibilityChartNote compatibilityChartNote = new CompatibilityChartNote();
                                  compatibilityChartNote.time = chartNote.time;
                                  compatibilityChartNote.type = chartNote.type;
                                  compatibilityChartNote.positionX = chartNote.positionX;
                                  compatibilityChartNote.holdTime = chartNote.holdTime;
                                  compatibilityChartNote.speed = chartNote.speed;
                                  compatibilityChartNote.floorPosition = chartNote.floorPosition;
                                  compatibilityJudgeLine.notesAbove.Add(compatibilityChartNote);
                                  if (compatibilityChartNote.type == 3)
                                  {
                                      compatibilityChartNote.speed = chartNote.headSpeed;
                                  }
                              }
                          }
                          compatibilityJudgeLine.notesBelow = new List<CompatibilityChartNote>();
                          if (chart.judgeLineList[num].notesBelow.Count > 0)
                          {
                              foreach (ChartNote chartNote2 in chart.judgeLineList[num].notesBelow)
                              {
                                  CompatibilityChartNote compatibilityChartNote2 = new CompatibilityChartNote();
                                  compatibilityChartNote2.time = chartNote2.time;
                                  compatibilityChartNote2.type = chartNote2.type;
                                  compatibilityChartNote2.positionX = chartNote2.positionX;
                                  compatibilityChartNote2.holdTime = chartNote2.holdTime;
                                  compatibilityChartNote2.speed = chartNote2.speed;
                                  compatibilityChartNote2.floorPosition = chartNote2.floorPosition;
                                  compatibilityJudgeLine.notesBelow.Add(compatibilityChartNote2);
                                  if (compatibilityChartNote2.type == 3)
                                  {
                                      compatibilityChartNote2.speed = chartNote2.headSpeed;
                                  }
                              }
                          }
                          compatibilityJudgeLine.speedEvents = new List<CompatibilitySpeedEvent>();
                          CompatibilitySpeedEvent compatibilitySpeedEvent = new CompatibilitySpeedEvent();
                          if (chart.judgeLineList[num].speedEvents.Count > 0)
                          {
                              for (int j = 0; j < chart.judgeLineList[num].speedEvents.Count; j++)
                              {
                                  SpeedEvent speedEvent = chart.judgeLineList[num].speedEvents[j];
                                  if (j == 0 && speedEvent.startTime != 0f)
                                  {
                                      compatibilitySpeedEvent = new CompatibilitySpeedEvent();
                                      compatibilitySpeedEvent.startTime = 0f;
                                      compatibilitySpeedEvent.endTime = speedEvent.startTime;
                                      compatibilitySpeedEvent.floorPosition = 0f;
                                      compatibilitySpeedEvent.value = 1f;
                                      compatibilityJudgeLine.speedEvents.Add(compatibilitySpeedEvent);
                                  }
                                  compatibilitySpeedEvent = new CompatibilitySpeedEvent();
                                  compatibilitySpeedEvent.startTime = speedEvent.startTime;
                                  compatibilitySpeedEvent.endTime = ((j < chart.judgeLineList[num].speedEvents.Count - 1) ? chart.judgeLineList[num].speedEvents[j + 1].startTime   : 1E+09f);
                                  compatibilitySpeedEvent.floorPosition = speedEvent.floorPosition;
                                  compatibilitySpeedEvent.value = speedEvent.value;
                                  compatibilityJudgeLine.speedEvents.Add(compatibilitySpeedEvent);
                              }
                          }
                          else
                          {
                              compatibilitySpeedEvent = new CompatibilitySpeedEvent();
                              compatibilitySpeedEvent.startTime = 0f;
                              compatibilitySpeedEvent.endTime = 1E+09f;
                              compatibilitySpeedEvent.floorPosition = 0f;
                              compatibilitySpeedEvent.value = 1f;
                              compatibilityJudgeLine.speedEvents.Add(compatibilitySpeedEvent);
                          }
                          compatibilityJudgeLine.judgeLineDisappearEvents = new List<CompatibilityJudgeLineEvent>();
                          CompatibilityJudgeLineEvent compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                          compatibilityJudgeLineEvent.startTime = -999999f;
                          compatibilityJudgeLineEvent.endTime = 1E+09f;
                          compatibilityJudgeLineEvent.start = 0f;
                          compatibilityJudgeLineEvent.end = 0f;
                          compatibilityJudgeLine.judgeLineDisappearEvents.Add(compatibilityJudgeLineEvent);
                          for (int k = 0; k < chart.judgeLineList[num].judgeLineDisappearEvents.Count; k++)
                          {
                              if (k == 0)
                              {
                                  compatibilityJudgeLine.judgeLineDisappearEvents[0].start = chart.judgeLineList[num].judgeLineDisappearEvents[k].start;
                                  compatibilityJudgeLine.judgeLineDisappearEvents[0].end = chart.judgeLineList[num].judgeLineDisappearEvents[k].start;
                                  compatibilityJudgeLine.judgeLineDisappearEvents[0].endTime = chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime;
                              }
                              if (k < chart.judgeLineList[num].judgeLineDisappearEvents.Count - 1)
                              {
                                  if (chart.judgeLineList[num].judgeLineDisappearEvents[k].easeType == 0)
                                  {
                                      compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                      compatibilityJudgeLineEvent.startTime = chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime;
                                      compatibilityJudgeLineEvent.endTime = chart.judgeLineList[num].judgeLineDisappearEvents[k + 1].startTime;
                                      compatibilityJudgeLineEvent.start = chart.judgeLineList[num].judgeLineDisappearEvents[k].start;
                                      compatibilityJudgeLineEvent.end = (chart.judgeLineList[num].judgeLineDisappearEvents[k].useEndNode ? chart.judgeLineList[num].  judgeLineDisappearEvents[k].end : chart.judgeLineList[num].judgeLineDisappearEvents[k + 1].start);
                                      compatibilityJudgeLine.judgeLineDisappearEvents.Add(compatibilityJudgeLineEvent);
                                  }
                                  else
                                  {
                                      int num2 = 0;
                                      while ((float)num2 + chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime < chart.judgeLineList[num].judgeLineDisappearEvents[k +   1].startTime)
                                      {
                                          compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                          compatibilityJudgeLineEvent.startTime = (float)num2 + chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime;
                                          compatibilityJudgeLineEvent.start = this.GetEaseProgress(chart.judgeLineList[num].judgeLineDisappearEvents[k].easeType,   (compatibilityJudgeLineEvent.startTime - chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime) / (chart.judgeLineList[num].  judgeLineDisappearEvents[k + 1].startTime - chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime)) * ((chart.judgeLineList  [num].judgeLineDisappearEvents[k].useEndNode ? chart.judgeLineList[num].judgeLineDisappearEvents[k].end : chart.judgeLineList[num].  judgeLineDisappearEvents[k + 1].start) - chart.judgeLineList[num].judgeLineDisappearEvents[k].start) + chart.judgeLineList[num].  judgeLineDisappearEvents[k].start;
                                          if (compatibilityJudgeLineEvent.startTime != chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime)
                                          {
                                              compatibilityJudgeLine.judgeLineDisappearEvents[compatibilityJudgeLine.judgeLineDisappearEvents.Count - 1].endTime =   compatibilityJudgeLineEvent.startTime;
                                              compatibilityJudgeLine.judgeLineDisappearEvents[compatibilityJudgeLine.judgeLineDisappearEvents.Count - 1].end =   compatibilityJudgeLineEvent.start;
                                          }
                                          compatibilityJudgeLineEvent.endTime = chart.judgeLineList[num].judgeLineDisappearEvents[k + 1].startTime;
                                          compatibilityJudgeLineEvent.end = this.GetEaseProgress(chart.judgeLineList[num].judgeLineDisappearEvents[k].easeType, 1f) * ((chart.  judgeLineList[num].judgeLineDisappearEvents[k].useEndNode ? chart.judgeLineList[num].judgeLineDisappearEvents[k].end : chart.  judgeLineList[num].judgeLineDisappearEvents[k + 1].start) - chart.judgeLineList[num].judgeLineDisappearEvents[k].start) + chart.  judgeLineList[num].judgeLineDisappearEvents[k].start;
                                          compatibilityJudgeLine.judgeLineDisappearEvents.Add(compatibilityJudgeLineEvent);
                                          if (chart.judgeLineList[num].judgeLineDisappearEvents[k + 1].startTime - chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime   >= 512f)
                                          {
                                              num2 += 16;
                                          }
                                          else if (chart.judgeLineList[num].judgeLineDisappearEvents[k + 1].startTime - chart.judgeLineList[num].judgeLineDisappearEvents[k].  startTime >= 256f)
                                          {
                                              num2 += 8;
                                          }
                                          else if (chart.judgeLineList[num].judgeLineDisappearEvents[k + 1].startTime - chart.judgeLineList[num].judgeLineDisappearEvents[k].  startTime >= 128f)
                                          {
                                              num2 += 4;
                                          }
                                          else
                                          {
                                              num2++;
                                          }
                                      }
                                  }
                              }
                              else
                              {
                                  compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                  compatibilityJudgeLineEvent.startTime = chart.judgeLineList[num].judgeLineDisappearEvents[k].startTime;
                                  compatibilityJudgeLineEvent.endTime = 1E+09f;
                                  compatibilityJudgeLineEvent.start = chart.judgeLineList[num].judgeLineDisappearEvents[k].start;
                                  compatibilityJudgeLineEvent.end = compatibilityJudgeLineEvent.start;
                                  compatibilityJudgeLine.judgeLineDisappearEvents.Add(compatibilityJudgeLineEvent);
                              }
                          }
                          compatibilityJudgeLine.judgeLineRotateEvents = new List<CompatibilityJudgeLineEvent>();
                          compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                          compatibilityJudgeLineEvent.startTime = -999999f;
                          compatibilityJudgeLineEvent.endTime = 1E+09f;
                          compatibilityJudgeLineEvent.start = 0f;
                          compatibilityJudgeLineEvent.end = 0f;
                          compatibilityJudgeLine.judgeLineRotateEvents.Add(compatibilityJudgeLineEvent);
                          for (int l = 0; l < chart.judgeLineList[num].judgeLineRotateEvents.Count; l++)
                          {
                              if (l == 0)
                              {
                                  compatibilityJudgeLine.judgeLineRotateEvents[0].start = chart.judgeLineList[num].judgeLineRotateEvents[l].start;
                                  compatibilityJudgeLine.judgeLineRotateEvents[0].end = chart.judgeLineList[num].judgeLineRotateEvents[l].start;
                                  compatibilityJudgeLine.judgeLineRotateEvents[0].endTime = chart.judgeLineList[num].judgeLineRotateEvents[l].startTime;
                              }
                              if (l < chart.judgeLineList[num].judgeLineRotateEvents.Count - 1)
                              {
                                  if (chart.judgeLineList[num].judgeLineRotateEvents[l].easeType == 0)
                                  {
                                      compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                      compatibilityJudgeLineEvent.startTime = chart.judgeLineList[num].judgeLineRotateEvents[l].startTime;
                                      compatibilityJudgeLineEvent.endTime = chart.judgeLineList[num].judgeLineRotateEvents[l + 1].startTime;
                                      compatibilityJudgeLineEvent.start = chart.judgeLineList[num].judgeLineRotateEvents[l].start;
                                      compatibilityJudgeLineEvent.end = (chart.judgeLineList[num].judgeLineRotateEvents[l].useEndNode ? chart.judgeLineList[num].  judgeLineRotateEvents[l].end : chart.judgeLineList[num].judgeLineRotateEvents[l + 1].start);
                                      compatibilityJudgeLine.judgeLineRotateEvents.Add(compatibilityJudgeLineEvent);
                                  }
                                  else
                                  {
                                      int num2 = 0;
                                      while ((float)num2 + chart.judgeLineList[num].judgeLineRotateEvents[l].startTime < chart.judgeLineList[num].judgeLineRotateEvents[l + 1].  startTime)
                                      {
                                          compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                          compatibilityJudgeLineEvent.startTime = (float)num2 + chart.judgeLineList[num].judgeLineRotateEvents[l].startTime;
                                          compatibilityJudgeLineEvent.start = this.GetEaseProgress(chart.judgeLineList[num].judgeLineRotateEvents[l].easeType,   (compatibilityJudgeLineEvent.startTime - chart.judgeLineList[num].judgeLineRotateEvents[l].startTime) / (chart.judgeLineList[num].  judgeLineRotateEvents[l + 1].startTime - chart.judgeLineList[num].judgeLineRotateEvents[l].startTime)) * ((chart.judgeLineList[num].  judgeLineRotateEvents[l].useEndNode ? chart.judgeLineList[num].judgeLineRotateEvents[l].end : chart.judgeLineList[num].  judgeLineRotateEvents[l + 1].start) - chart.judgeLineList[num].judgeLineRotateEvents[l].start) + chart.judgeLineList[num].  judgeLineRotateEvents[l].start;
                                          if (compatibilityJudgeLineEvent.startTime != chart.judgeLineList[num].judgeLineRotateEvents[l].startTime)
                                          {
                                              compatibilityJudgeLine.judgeLineRotateEvents[compatibilityJudgeLine.judgeLineRotateEvents.Count - 1].endTime =   compatibilityJudgeLineEvent.startTime;
                                              compatibilityJudgeLine.judgeLineRotateEvents[compatibilityJudgeLine.judgeLineRotateEvents.Count - 1].end =   compatibilityJudgeLineEvent.start;
                                          }
                                          compatibilityJudgeLineEvent.endTime = chart.judgeLineList[num].judgeLineRotateEvents[l + 1].startTime;
                                          compatibilityJudgeLineEvent.end = this.GetEaseProgress(chart.judgeLineList[num].judgeLineRotateEvents[l].easeType, 1f) * ((chart.  judgeLineList[num].judgeLineRotateEvents[l].useEndNode ? chart.judgeLineList[num].judgeLineRotateEvents[l].end : chart.judgeLineList  [num].judgeLineRotateEvents[l + 1].start) - chart.judgeLineList[num].judgeLineRotateEvents[l].start) + chart.judgeLineList[num].  judgeLineRotateEvents[l].start;
                                          compatibilityJudgeLine.judgeLineRotateEvents.Add(compatibilityJudgeLineEvent);
                                          if (chart.judgeLineList[num].judgeLineRotateEvents[l + 1].startTime - chart.judgeLineList[num].judgeLineRotateEvents[l].startTime >=   512f)
                                          {
                                              num2 += 16;
                                          }
                                          else if (chart.judgeLineList[num].judgeLineRotateEvents[l + 1].startTime - chart.judgeLineList[num].judgeLineRotateEvents[l].startTime   >= 256f)
                                          {
                                              num2 += 8;
                                          }
                                          else if (chart.judgeLineList[num].judgeLineRotateEvents[l + 1].startTime - chart.judgeLineList[num].judgeLineRotateEvents[l].startTime   >= 128f)
                                          {
                                              num2 += 4;
                                          }
                                          else
                                          {
                                              num2++;
                                          }
                                      }
                                  }
                              }
                              else
                              {
                                  compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                  compatibilityJudgeLineEvent.startTime = chart.judgeLineList[num].judgeLineRotateEvents[l].startTime;
                                  compatibilityJudgeLineEvent.endTime = 1E+09f;
                                  compatibilityJudgeLineEvent.start = chart.judgeLineList[num].judgeLineRotateEvents[l].start;
                                  compatibilityJudgeLineEvent.end = compatibilityJudgeLineEvent.start;
                                  compatibilityJudgeLine.judgeLineRotateEvents.Add(compatibilityJudgeLineEvent);
                              }
                          }
                          compatibilityJudgeLine.judgeLineMoveEvents = new List<CompatibilityJudgeLineEvent>();
                          compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                          compatibilityJudgeLineEvent.startTime = -999999f;
                          compatibilityJudgeLineEvent.endTime = 1E+09f;
                          compatibilityJudgeLineEvent.start = 0.5f;
                          compatibilityJudgeLineEvent.start2 = 0.5f;
                          compatibilityJudgeLineEvent.end = 0.5f;
                          compatibilityJudgeLineEvent.end2 = 0.5f;
                          compatibilityJudgeLine.judgeLineMoveEvents.Add(compatibilityJudgeLineEvent);
                          for (int m = 0; m < chart.judgeLineList[num].judgeLineMoveEvents.Count; m++)
                          {
                              if (m == 0)
                              {
                                  compatibilityJudgeLine.judgeLineMoveEvents[0].start = chart.judgeLineList[num].judgeLineMoveEvents[m].start;
                                  compatibilityJudgeLine.judgeLineMoveEvents[0].start2 = chart.judgeLineList[num].judgeLineMoveEvents[m].start2;
                                  compatibilityJudgeLine.judgeLineMoveEvents[0].end = compatibilityJudgeLine.judgeLineMoveEvents[0].start;
                                  compatibilityJudgeLine.judgeLineMoveEvents[0].end2 = compatibilityJudgeLine.judgeLineMoveEvents[0].start2;
                                  compatibilityJudgeLine.judgeLineMoveEvents[0].endTime = chart.judgeLineList[num].judgeLineMoveEvents[m].startTime;
                              }
                              if (m < chart.judgeLineList[num].judgeLineMoveEvents.Count - 1)
                              {
                                  if (chart.judgeLineList[num].judgeLineMoveEvents[m].easeType == 0 && chart.judgeLineList[num].judgeLineMoveEvents[m].easeType2 == 0)
                                  {
                                      compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                      compatibilityJudgeLineEvent.startTime = chart.judgeLineList[num].judgeLineMoveEvents[m].startTime;
                                      compatibilityJudgeLineEvent.endTime = chart.judgeLineList[num].judgeLineMoveEvents[m + 1].startTime;
                                      compatibilityJudgeLineEvent.start = chart.judgeLineList[num].judgeLineMoveEvents[m].start;
                                      compatibilityJudgeLineEvent.start2 = chart.judgeLineList[num].judgeLineMoveEvents[m].start2;
                                      compatibilityJudgeLineEvent.end = (chart.judgeLineList[num].judgeLineMoveEvents[m].useEndNode ? chart.judgeLineList[num].judgeLineMoveEvents  [m].end : chart.judgeLineList[num].judgeLineMoveEvents[m + 1].start);
                                      compatibilityJudgeLineEvent.end2 = (chart.judgeLineList[num].judgeLineMoveEvents[m].useEndNode ? chart.judgeLineList[num].judgeLineMoveEvents  [m].end2 : chart.judgeLineList[num].judgeLineMoveEvents[m + 1].start2);
                                      compatibilityJudgeLine.judgeLineMoveEvents.Add(compatibilityJudgeLineEvent);
                                  }
                                  else
                                  {
                                      int num2 = 0;
                                      while ((float)num2 + chart.judgeLineList[num].judgeLineMoveEvents[m].startTime < chart.judgeLineList[num].judgeLineMoveEvents[m + 1].  startTime)
                                      {
                                          compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                          compatibilityJudgeLineEvent.startTime = (float)num2 + chart.judgeLineList[num].judgeLineMoveEvents[m].startTime;
                                          compatibilityJudgeLineEvent.start = this.GetEaseProgress(chart.judgeLineList[num].judgeLineMoveEvents[m].easeType,   (compatibilityJudgeLineEvent.startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime) / (chart.judgeLineList[num].  judgeLineMoveEvents[m + 1].startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime)) * ((chart.judgeLineList[num].  judgeLineMoveEvents[m].useEndNode ? chart.judgeLineList[num].judgeLineMoveEvents[m].end : chart.judgeLineList[num].judgeLineMoveEvents[m   + 1].start) - chart.judgeLineList[num].judgeLineMoveEvents[m].start) + chart.judgeLineList[num].judgeLineMoveEvents[m].start;
                                          compatibilityJudgeLineEvent.start2 = this.GetEaseProgress(chart.judgeLineList[num].judgeLineMoveEvents[m].easeType2,   (compatibilityJudgeLineEvent.startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime) / (chart.judgeLineList[num].  judgeLineMoveEvents[m + 1].startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime)) * ((chart.judgeLineList[num].  judgeLineMoveEvents[m].useEndNode ? chart.judgeLineList[num].judgeLineMoveEvents[m].end2 : chart.judgeLineList[num].judgeLineMoveEvents  [m + 1].start2) - chart.judgeLineList[num].judgeLineMoveEvents[m].start2) + chart.judgeLineList[num].judgeLineMoveEvents[m].start2;
                                          if (compatibilityJudgeLineEvent.startTime != chart.judgeLineList[num].judgeLineMoveEvents[m].startTime)
                                          {
                                              compatibilityJudgeLine.judgeLineMoveEvents[compatibilityJudgeLine.judgeLineMoveEvents.Count - 1].endTime =   compatibilityJudgeLineEvent.startTime;
                                              compatibilityJudgeLine.judgeLineMoveEvents[compatibilityJudgeLine.judgeLineMoveEvents.Count - 1].end = compatibilityJudgeLineEvent.  start;
                                              compatibilityJudgeLine.judgeLineMoveEvents[compatibilityJudgeLine.judgeLineMoveEvents.Count - 1].end2 = compatibilityJudgeLineEvent.  start2;
                                          }
                                          compatibilityJudgeLineEvent.endTime = chart.judgeLineList[num].judgeLineMoveEvents[m + 1].startTime;
                                          compatibilityJudgeLineEvent.end = this.GetEaseProgress(chart.judgeLineList[num].judgeLineMoveEvents[m].easeType, 1f) * ((chart.  judgeLineList[num].judgeLineMoveEvents[m].useEndNode ? chart.judgeLineList[num].judgeLineMoveEvents[m].end : chart.judgeLineList[num].  judgeLineMoveEvents[m + 1].start) - chart.judgeLineList[num].judgeLineMoveEvents[m].start) + chart.judgeLineList[num].judgeLineMoveEvents  [m].start;
                                          compatibilityJudgeLineEvent.end2 = this.GetEaseProgress(chart.judgeLineList[num].judgeLineMoveEvents[m].easeType2, 1f) * ((chart.  judgeLineList[num].judgeLineMoveEvents[m].useEndNode ? chart.judgeLineList[num].judgeLineMoveEvents[m].end2 : chart.judgeLineList[num].  judgeLineMoveEvents[m + 1].start2) - chart.judgeLineList[num].judgeLineMoveEvents[m].start2) + chart.judgeLineList[num].  judgeLineMoveEvents[m].start2;
                                          compatibilityJudgeLine.judgeLineMoveEvents.Add(compatibilityJudgeLineEvent);
                                          if (chart.judgeLineList[num].judgeLineMoveEvents[m + 1].startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime >= 512f)
                                          {
                                              num2 += 16;
                                          }
                                          else if (chart.judgeLineList[num].judgeLineMoveEvents[m + 1].startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime >=   256f)
                                          {
                                              num2 += 8;
                                          }
                                          else if (chart.judgeLineList[num].judgeLineMoveEvents[m + 1].startTime - chart.judgeLineList[num].judgeLineMoveEvents[m].startTime >=   128f)
                                          {
                                              num2 += 4;
                                          }
                                          else
                                          {
                                              num2++;
                                          }
                                      }
                                  }
                              }
                              else
                              {
                                  compatibilityJudgeLineEvent = new CompatibilityJudgeLineEvent();
                                  compatibilityJudgeLineEvent.startTime = chart.judgeLineList[num].judgeLineMoveEvents[m].startTime;
                                  compatibilityJudgeLineEvent.endTime = 1E+09f;
                                  compatibilityJudgeLineEvent.start = chart.judgeLineList[num].judgeLineMoveEvents[m].start;
                                  compatibilityJudgeLineEvent.start2 = chart.judgeLineList[num].judgeLineMoveEvents[m].start2;
                                  compatibilityJudgeLineEvent.end = compatibilityJudgeLineEvent.start;
                                  compatibilityJudgeLineEvent.end2 = compatibilityJudgeLineEvent.start2;
                                  compatibilityJudgeLine.judgeLineMoveEvents.Add(compatibilityJudgeLineEvent);
                              }
                          }
                          compatibilityChart.judgeLineList.Add(compatibilityJudgeLine);
                          num++;
                      }
                      string text = Application.dataPath.Substring(0, Application.dataPath.LastIndexOf("/")) + "/Compatibility_Charts/【全难度】" + this.projectInfo.songName;
                      if (!Directory.Exists(text))
                      {
                          Directory.CreateDirectory(text);
                      }
                      string path = text + str;
                      if (!File.Exists(path))
                      {
                          FileStream fileStream = File.Create(path);
                          fileStream.Close();
                          fileStream.Dispose();
                      }
                      string contents = JsonUtility.ToJson(compatibilityChart, false);
                      File.WriteAllText(path, contents);
                  }
              }
          }
  
          public float GetEaseProgress(int easeType, float progress)
          {
              if (progress <= 0f) return 0f;
              if (progress >= 1f) return 1f;
              return (float)easeInfors[easeType].progress[(int)(progress * 100f) + 1] / 100f;
          }
      }
  }
  ```

</details>

## PhiEdit Chart

`pec` 谱面为命令型文本格式，通常读取文件到 `str`, 然后使用 `\n` 分割为数组。

对于谱面第一行，表示为谱面 `offset`，单位为 `ms`，减去 `150` 即可转化为 `rpe` 格式的 `offset`。

例如: `pec` 文件第一行为 `150`，则 `offset` 为 `150 - 150 = 0 (ms)`。

读取完成 `offset` 后可删除第一行，以便于后续读取。

<details>
  <summary>这种谱面规范吗 （？</summary>

  在一些谱面中, 需要将 `" #"` 替换为 `"\n#"`, `" &"` 替换为 `"\n&"`。
</details>

每行可被 `" " (空格)` 分割为许多 `token`，我们跳过空行。

至此，我们得到了一个 `token` 数组，即 `list[list[str]]`。

我们定义:

```python
rpex = lambda x: (x / 2048 - 0.5) * 1350
rpey = lambda y: (y / 1400 -  0.5) * 900
rpes = lambda s: s / 1400 * 900

def pec2rpe_findevent_bytime(events: list[dict], t: float, default: float):
    """用于瞬时事件后的事件寻找开始值。"""
    if not events: return default
    
    ets = list(map(lambda x: abs(x["endTime"][0] - t), events))
    return events[ets.index(min(ets))]["end"]
```

格式说明 (对于第一个 `token`):

- `bp`

    表示谱面 `bpm` 事件，格式为 `bp startTime bpm`。

    类型为 `bp <float> <float>`。

    对应的 `rpe` 格式为:

    ```python
    {
        "startTime": [float(tokens[1]), 0, 1],
        "bpm": [float(tokens[2]), 0, 1]
    }
    ```

- `n1` & `n2` & `n3` & `n4`

    表示判定线 `note`。

    对于 `n2 (hold)`，格式为 `n2 lineIndex startTime endTime positionX isAbove isFake`，
    
    类型为 `n2 <int> <float> <float> <float> <int> <int>`。

    对于其他, 格式为 `n1 lineIndex startTime positionX isAbove isFake`，

    类型为 `n1 <int> <float> <float> <int> <int>`。

    该命令的下两行为 `speed` 和 `size`，格式为 `# speed` `& size`。

    示例：

    ```txt
    n2 0 10 15 0 1 0
    # 1.2
    & 1.4
    ```

    转化为 `rpe` 格式为:

    ```python
    et = None
    if tokens[0] == "n2":
        et = [float(tokens.pop(3)), 0, 1]
    
    ntype = {"n1": 1, "n2": 2, "n3": 3, "n4": 4}[tokens[0]]
    k = int(tokens[1])
    st = [float(tokens[2]), 0, 1]
    x = float(tokens[3])

    if et is None: et = st.copy()

    above = int(tokens[4])
    fake = bool(int(tokens[5]))
    speed = float(speed) # 例如该命令的一下行为 `# 1.2`, 则 speed 为 `1.2`
    size = float(size) # 例如该命令的一下行为 `& 1.4`, 则 size 为 `1.4`

    judgeLineList[k]["notes"].append({
        "type": ntype,
        "startTime": st,
        "endTime": et,
        "positionX": x / 2048 * 1350,
        "above": above,
        "isFake": fake,
        "speed": speed,
        "size": size
    })
    ```

- `cp`

    表示判定线瞬时移动事件，格式为 `cp lineIndex time x y`，

    类型为 `cp <int> <float> <float> <float>`。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    st = [float(tokens[2]), 0, 1]
    x = float(tokens[3])
    y = float(tokens[4])

    judgeLineList[k]["eventLayers"][0]["moveXEvents"].append({
        "startTime": t, "endTime": t,
        "start": rpex(x), "end": rpex(x),
        "easingType": 1
    })

    judgeLineList[k]["eventLayers"][0]["moveYEvents"].append({
        "startTime": t, "endTime": t,
        "start": rpey(y), "end": rpey(y),
        "easingType": 1
    })
    ```

- `cd`

    表示判定线瞬时旋转事件, 格式为 `cd lineIndex time deg`，

    类型为 `cd <int> <float> <float>`。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    t = [float(tokens[2]), 0, 1]
    v = float(tokens[3])

    judgeLineList[k]["eventLayers"][0]["rotateEvents"].append({
        "startTime": t, "endTime": t,
        "start": v, "end": v,
        "easingType": 1
    })
    ```

- `ca`

    表示判定线瞬时透明度事件，格式为 `ca lineIndex time alpha`，

    类型为 `ca <int> <float> <float>`。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    t = [float(tokens[2]), 0, 1]
    v = float(tokens[3])

    judgeLineList[k]["eventLayers"][0]["alphaEvents"].append({
        "startTime": t, "endTime": t,
        "start": v, "end": v,
        "easingType": 1
    })

- `cv`

    表示判定线瞬时速度事件, 格式为 `cv lineIndex time speed`，

    类型为 `cv <int> <float> <float>`。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    t = [float(tokens[2]), 0, 1]
    v = float(tokens[3])

    judgeLineList[k]["eventLayers"][0]["speedEvents"].append({
        "startTime": t, "endTime": t,
        "start": v, "end": v,
        "easingType": 1
    })
    ```

- `cm`

    表示判定线移动事件, 格式为 `cm lineIndex startTime endTime endX endY ease`，

    类型为 `cm <int> <float> <float> <float> <float> <int>`。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    st = [float(tokens[2]), 0, 1]
    et = [float(tokens[3]), 0, 1]
    ex = float(tokens[4])
    ey = float(tokens[5])
    ease = int(tokens[6])

    mxes = judgeLineList[k]["eventLayers"][0]["moveXEvents"]
    myes = judgeLineList[k]["eventLayers"][0]["moveYEvents"]
    sx = pec2rpe_findevent_bytime(mxes, st[0], rpex(ex))
    sy = pec2rpe_findevent_bytime(myes, st[0], rpey(ey))
    
    mxes.append({
        "startTime": st, "endTime": et,
        "start": sx, "end": rpex(ex),
        "easingType": ease
    })

    myes.append({
        "startTime": st, "endTime": et,
        "start": sy, "end": rpey(ey),
        "easingType": ease
    })
    ```

- `cr`

    表示判定线旋转事件, 格式为 `cr lineIndex startTime endTime endDeg ease`，

    格式为 `cr <int> <float> <float> <float> <int>`。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    st = [float(tokens[2]), 0, 1]
    et = [float(tokens[3]), 0, 1]
    ev = float(tokens[4])
    ease = int(tokens[5])

    res = judgeLineList[k]["eventLayers"][0]["rotateEvents"]
    sv = pec2rpe_findevent_bytime(res, st[0], ev)

    res.append({
        "startTime": st, "endTime": et,
        "start": sv, "end": ev,
        "easingType": ease
    })
    ```

- `cf`

    表示判定线透明度事件, 格式为 `cf lineIndex startTime endTime endAlpha`，

    格式为 `cf <int> <float> <float> <float>`。

    是不是觉得怪怪的？ 对！, `cf` 居然没有 `ease` 参数。

    对应的 `rpe` 格式为:

    ```python
    k = int(tokens[1])
    st = [float(tokens[2]), 0, 1]
    et = [float(tokens[3]), 0, 1]
    ev = float(tokens[4])

    aes = judgeLineList[k]["eventLayers"][0]["alphaEvents"]
    sv = pec2rpe_findevent_bytime(aes, st[0], ev)

    aes.append({
        "startTime": st, "endTime": et,
        "start": sv, "end": ev,
        "easingType": 1
    })
    ```

至此，我们了解了 `pec` 文件的格式，为保证文档的严谨性, 在此贴出 `pec` 转 `rpe` 格式的 `python` 示例代码 (为最小化 `rpe` 格式, 默认项省略):

<details>
  <summary>展开</summary>

  ```python

  def isallnum(lst: list[str], l: int|None = None):
        return (len(lst) >= l or l is None) and all(map(lambda x: isfloatable(x), lst))

  def pec2rpe_findevent_bytime(es: list[dict], t: float, default: float):
      if not es: return default
      
      ets = list(map(lambda x: abs(x["endTime"][0] - t), es))
      return es[ets.index(min(ets))]["end"]
  
  def pec2rpe(pec: str):
      errs = []
      peclines = pec.replace(" #", "\n#").replace(" &", "\n&").split("\n")
      result = {
          "META": {},
          "BPMList": [],
          "judgeLineList": []
      }
      
      result["META"]["offset"] = float(peclines.pop(0)) - 150
      
      peclines = list(
          map(
              lambda x: list(filter(lambda x: x, x)),
              map(lambda x: x.split(" "), peclines)
          )
      )
      
      pecbpms = list(filter(lambda x: x and x[0] == "bp" and isallnum(x[1:], 2), peclines))
      pecnotes = list(filter(lambda x: x and x[0] in ("n1", "n2", "n3", "n4") and isallnum(x[1:], 5 if x[0] != "n2" else 6), peclines))
      pecnotespeeds = list(filter(lambda x: x and x[0] == "#" and isallnum(x[1:], 1), peclines))
      pecnotesizes = list(filter(lambda x: x and x[0] == "&" and isallnum(x[1:], 1), peclines))
      peccps = list(filter(lambda x: x and x[0] == "cp" and isallnum(x[1:], 4), peclines))
      peccds = list(filter(lambda x: x and x[0] == "cd" and isallnum(x[1:], 3), peclines))
      peccas = list(filter(lambda x: x and x[0] == "ca" and isallnum(x[1:], 3), peclines))
      peccvs = list(filter(lambda x: x and x[0] == "cv" and isallnum(x[1:], 3), peclines))
      peccms = list(filter(lambda x: x and x[0] == "cm" and isallnum(x[1:], 6), peclines))
      peccrs = list(filter(lambda x: x and x[0] == "cr" and isallnum(x[1:], 5), peclines))
      peccfs = list(filter(lambda x: x and x[0] == "cf" and isallnum(x[1:], 4), peclines))
      
      pecbpms.sort(key = lambda x: float(x[1]))
      
      notezip = list(zip(pecnotes, pecnotespeeds, pecnotesizes))
      notezip.sort(key = lambda x: float(x[0][2]))
      
      peccps.sort(key = lambda x: float(x[1]))
      peccds.sort(key = lambda x: float(x[1]))
      peccas.sort(key = lambda x: float(x[1]))
      peccvs.sort(key = lambda x: float(x[1]))
      peccms.sort(key = lambda x: float(x[1]))
      peccrs.sort(key = lambda x: float(x[1]))
      peccfs.sort(key = lambda x: float(x[1]))
      
      rpex = lambda x: (x / 2048 - 0.5) * const.RPE_WIDTH
      rpey = lambda y: (y / 1400 -  0.5) * const.RPE_HEIGHT
      rpes = lambda s: s / 1400 * const.RPE_HEIGHT
      lines = {}
      
      checkLine = lambda k: [
          (
              lines.update({k: {
                  "eventLayers": [{
                      "speedEvents": [],
                      "moveXEvents": [],
                      "moveYEvents": [],
                      "rotateEvents": [],
                      "alphaEvents": []
                  }],
                  "notes": []
              }}),
              result["judgeLineList"].append(lines[k])
          ) if k not in lines else None,
      ]
      
      for e in pecbpms:
          try:
              result["BPMList"].append({
                  "startTime": [float(e[1]), 0, 1],
                  "bpm": float(e[2])
              })
          except Exception as e:
              errs.append(e)
      
      for e, sp, si in notezip:
          try:
              et = None
              if e[0] == "n2": et = [float(e.pop(3)), 0, 1]
              ntype = {"n1": 1, "n2": 2, "n3": 3, "n4": 4}[e[0]]
              k = int(e[1])
              st = [float(e[2]), 0, 1]
              x = float(e[3])
              if et is None: et = st.copy()
              above = int(e[4])
              fake = bool(int(e[5]))
              speed = float(sp[1])
              size = float(si[1])
              
              checkLine(k)
              lines[k]["notes"].append({
                  "type": ntype,
                  "startTime": st,
                  "endTime": et,
                  "positionX": x / 2048 * const.RPE_WIDTH,
                  "above": above,
                  "isFake": fake,
                  "speed": speed,
                  "size": size
              })
          except Exception as e:
              errs.append(e)
      
      for e in peccps:
          try:
              k = int(e[1])
              t = [float(e[2]), 0, 1]
              x = float(e[3])
              y = float(e[4])
              
              checkLine(k)
              lines[k]["eventLayers"][0]["moveXEvents"].append({
                  "startTime": t, "endTime": t,
                  "start": rpex(x), "end": rpex(x),
                  "easingType": 1
              })
              lines[k]["eventLayers"][0]["moveYEvents"].append({
                  "startTime": t, "endTime": t,
                  "start": rpey(y), "end": rpey(y),
                  "easingType": 1
              })
          except Exception as e:
              errs.append(e)
  
      for e in peccds:
          try:
              k = int(e[1])
              t = [float(e[2]), 0, 1]
              v = float(e[3])
              
              checkLine(k)
              lines[k]["eventLayers"][0]["rotateEvents"].append({
                  "startTime": t, "endTime": t,
                  "start": v, "end": v,
                  "easingType": 1
              })
          except Exception as e:
              errs.append(e)
      
      for e in peccas:
          try:
              k = int(e[1])
              t = [float(e[2]), 0, 1]
              v = float(e[3])
  
              checkLine(k)
              lines[k]["eventLayers"][0]["alphaEvents"].append({
                  "startTime": t, "endTime": t,
                  "start": v, "end": v,
                  "easingType": 1
              })
          except Exception as e:
              errs.append(e)
      
      for e in peccvs:
          try:
              k = int(e[1])
              t = [float(e[2]), 0, 1]
              v = float(e[3])
  
              checkLine(k)
              lines[k]["eventLayers"][0]["speedEvents"].append({
                  "startTime": t, "endTime": t,
                  "start": rpes(v), "end": rpes(v),
                  "easingType": 1
              })
          except Exception as e:
              errs.append(e)
      
      for e in peccms:
          try:
              k = int(e[1])
              st = [float(e[2]), 0, 1]
              et = [float(e[3]), 0, 1]
              ex = float(e[4])
              ey = float(e[5])
              ease = int(e[6])
              
              checkLine(k)
              mxes = lines[k]["eventLayers"][0]["moveXEvents"]
              myes = lines[k]["eventLayers"][0]["moveYEvents"]
              sx = pec2rpe_findevent_bytime(mxes, st[0], rpex(ex))
              sy = pec2rpe_findevent_bytime(myes, st[0], rpey(ey))
  
              mxes.append({
                  "startTime": st, "endTime": et,
                  "start": sx, "end": rpex(ex),
                  "easingType": ease
              })
              myes.append({
                  "startTime": st, "endTime": et,
                  "start": sy, "end": rpey(ey),
                  "easingType": ease
              })
          except Exception as e:
              errs.append(e)
      
      for e in peccrs:
          try:
              k = int(e[1])
              st = [float(e[2]), 0, 1]
              et = [float(e[3]), 0, 1]
              ev = float(e[4])
              ease = int(e[5])
  
              checkLine(k)
              res = lines[k]["eventLayers"][0]["rotateEvents"]
              sv = pec2rpe_findevent_bytime(res, st[0], ev)
  
              res.append({
                  "startTime": st, "endTime": et,
                  "start": sv, "end": ev,
                  "easingType": ease
              })
          except Exception as e:
              errs.append(e)
      
      for e in peccfs:
          try:
              k = int(e[1])
              st = [float(e[2]), 0, 1]
              et = [float(e[3]), 0, 1]
              ev = float(e[4])
  
              checkLine(k)
              aes = lines[k]["eventLayers"][0]["alphaEvents"]
              sv = pec2rpe_findevent_bytime(aes, st[0], ev)
  
              aes.append({
                  "startTime": st, "endTime": et,
                  "start": sv, "end": ev,
                  "easingType": 1
              })
          except Exception as e:
              errs.append(e)
      
      return result, errs
  ```
</details>

## Re:PhiEdit 谱面
