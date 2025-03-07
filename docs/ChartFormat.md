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

`pec` 谱面为命令型文本格式, 通常读取文件到 `str`, 然后使用 `\n` 分割为数组。

对于谱面第一行, 表示为谱面 `offset`, 单位为 `ms`, 减去 `150` 即可转化为 `rpe` 格式的 `offset`。

例如: `pec` 文件第一行为 `150`, 则 `offset` 为 `150 - 150 = 0 (ms)`。

读取完成 `offset` 后可删除第一行, 以便于后续读取。

<details>
  <summary>这种谱面规范吗 （？</summary>

  在一些谱面中, 需要将 `" #"` 替换为 `"\n#"`, `" &"` 替换为 `"\n&"`。
</details>

每行可被 `" " (空格)` 分割为许多 `token`, 我们跳过空行。

至此, 我们得到了一个 `token` 数组, 即 `list[list[str]]`。

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

    表示谱面 `bpm` 事件, 格式为 `bp startTime bpm`。

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

    对于 `n2 (hold)`, 格式为 `n2 lineIndex startTime endTime positionX isAbove isFake`,

    类型为 `n2 <int> <float> <float> <float> <int> <int>`。

    对于其他, 格式为 `n1 lineIndex startTime positionX isAbove isFake`,

    类型为 `n1 <int> <float> <float> <int> <int>`。

    该命令的下两行为 `speed` 和 `size`, 格式为 `# speed` `& size`。

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

    表示判定线瞬时移动事件, 格式为 `cp lineIndex time x y`,

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

    表示判定线瞬时旋转事件, 格式为 `cd lineIndex time deg`,

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

    表示判定线瞬时透明度事件, 格式为 `ca lineIndex time alpha`,

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

    表示判定线瞬时速度事件, 格式为 `cv lineIndex time speed`,

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

    表示判定线移动事件, 格式为 `cm lineIndex startTime endTime endX endY ease`,

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

    表示判定线旋转事件, 格式为 `cr lineIndex startTime endTime endDeg ease`,

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

    表示判定线透明度事件, 格式为 `cf lineIndex startTime endTime endAlpha`,

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

至此, 我们了解了 `pec` 文件的格式, 为保证文档的严谨性, 在此贴出 `pec` 转 `rpe` 格式的 `python` 示例代码 (为最小化 `rpe` 格式, 默认项省略):

<details>
  <summary>展开</summary>

  ```python

  def isfloatable(s: str):
      try: float(s); return True
      except: return False

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

`rpe` 格式谱面为 `json` 格式。

（此处不介绍 < `140` 版本的任何特性）

谱面根结构:

- `BPMList`

    `list[dict]` 类型, 表示谱面的 `BPM` 列表。

- `META`

    `dict` 类型, 表示谱面的元数据。

- `judgeLineGroup`

    `list[str]` 类型, 表示谱面的判定线组。

    渲染不使用。

- `judgeLineList`

    `list[dict]` 类型, 表示谱面的判定线列表。

我们在此定义大小单位 `W` 与 `H`, 为屏幕的宽度与高度。

让我们了解一下 `BPMList`:

在此之前我们定义类型 `Beat` 与 `BPMEvent`:

```python
@dataclass
class Beat:
    v1: float; v2: float; v3: float
    
    def __post_init__(self):
        self.value = self.v1 + self.v2 / self.v3

@dataclass
class BPMEvent:
    startTime: Beat
    bpm: float
```

`Beat` 在谱面中的表示方式为 `[v1, v2, v3]`。

`BPMList` 的每个元素是一个 `dict`, 表示一个 `BPMEvent`。

例如:

```json5
{
    "BPMList": [
        {
            "bpm": 120,
            "startTime": [0, 0, 1] // 0 + 0 / 1 = 0
        },
        {
            "bpm": 180,
            "startTime": [16, 1, 2] // 16 + 1 / 2 = 16.5
        }
    ]
}
```

为确保文档的严谨性, 我们在此给出简单的秒与 `Beat` 的转换函数 (`bpmfactor` 在下文有所提及):

<details>
  <summary>展开</summary>

  ```python
  def sec2beat(t: float, bpmfactor: float, BPMList: list[BPMEvent]):
      beat = 0.0
      for i, e in enumerate(BPMList):
          bpmv = e.bpm / bpmfactor
          if i != len(BPMList) - 1:
              et_beat = BPMList[i + 1].startTime.value - e.startTime.value
              et_sec = et_beat * (60 / bpmv)
              
              if t >= et_sec:
                  beat += et_beat
                  t -= et_sec
              else:
                  beat += t / (60 / bpmv)
                  break
          else:
              beat += t / (60 / bpmv)
      return beat
  
  def beat2sec(t: float, bpmfactor: float, BPMList: list[BPMEvent]):
      sec = 0.0
      for i, e in enumerate(BPMList):
          bpmv = e.bpm / bpmfactor
          if i != len(BPMList) - 1:
              et_beat = BPMList[i + 1].startTime.value - e.startTime.value
              
              if t >= et_beat:
                  sec += et_beat * (60 / bpmv)
                  t -= et_beat
              else:
                  sec += t * (60 / bpmv)
                  break
          else:
              sec += t * (60 / bpmv)
      return sec
  ```

</details>

让我们了解一下 `META`:

- `RPEVersion`

    `int` 类型, 表示谱面的 `Re:PhiEdit` 版本。

    例如 `v1.4.0` 的版本号为 `140`。

- `offset`

    `int` 类型, 表示谱面的偏移量, 单位为 `ms`。

    计算方式与 `phi` 谱面一致。

- `name`

    `str` 类型, 表示谱面的名称。

    可在谱面渲染时用到。

    在 `phira` 中, 此字段优先级高于 `info` 文件。

- `id`

    `str` 类型, 表示谱面的 `id`。

    仅在 `Re:PhiEdit` 中使用。

    不影响渲染。

- `illustration`

    `str` 类型, 表示谱面的曲绘的 __作者__。

    `RPEVersion` > `141` 时存在。

    可在谱面加载动画渲染时用到。

    在 `phira` 中, 此字段优先级高于 `info` 文件。

    ~~ysj 不会 `illustrator` 是吧~~

- `song`

    `str` 类型, 表示谱面音频的相对路径, 辅助资源读取。

    例如 `123.ogg`。

- `background`

    `str` 类型, 表示谱面背景的相对路径, 辅助资源读取。

    例如 `123.png`。

- `composer`

    `str` 类型, 表示谱面的作曲家。

    可在谱面加载动画渲染时用到。

    在 `phira` 中, 此字段优先级高于 `info` 文件。

- `charter`

    `str` 类型, 表示谱面的谱师。

    可在谱面加载动画渲染时用到。

    在 `phira` 中, 此字段优先级高于 `info` 文件。

- `level`

    `int` 类型, 表示谱面的难度。

    可在谱面渲染时用到。

    在 `phira` 中, 此字段优先级高于 `info` 文件。

让我们了解一下 `judgeLineList` 的单个元素结构:

- `Group`

    `int` 类型, 表示判定线所属的判定线组。

    渲染不使用。

- `Name`

    `str` 类型, 表示判定线的名称。

    渲染不使用。

- `Texture`

    `str` 类型, 表示判定线的贴图的相对路径。

    默认为 `line.png`, 在 `Re:PhiEdit` 中为一张 `4000x5` 的图片, 推荐实际渲染时使用对于图形 `API` 绘制线, 而不是使用贴图。

    对于渲染时贴图的缩放, 我们假如图片大小实际为 `image_w` 与 `image_h`, 则实际渲染到屏幕上的大小为 (不考虑缩放):

    ```python
    real_w = image_w / 1350 * W
    real_h = real_w / image_w * image_h # 至少 Re:PhiEdit 是这样做的。
    ```

    对于判定线渲染, 我们不建议使用上面的缩放, 而是单独计算长与宽, 例如:

    ```python
    line_w = 4000 / 1350 * W
    line_h = 5 / 900 * H
    ```

- `bpmfactor`

    判定线的 `bpm` 速率。

    ！注意, 不是乘以这个值, 而是除以这个值！

    ~~你 ysj 的文档还写错 😡👊~~

- `alphaControl` & `posControl` & `sizeControl` & `skewControl` & `yControl`

    待补充, 行为难以确定。

- `father`

    `int` 类型, 表示判定线的父线。

    为 `-1` 是表示没有父线。

    不只是坐标相加, 而是改变坐标系原点, 更多的细节下文会解释。

- `isCover`

    `int` 类型, 表示判定线是否使用 `note` 遮罩。

    为 `0` 是表示不使用, 为 `1` 是表示使用。

    对于使用 `Re:PhiEdit` 生成的 `rpe` 谱面文件:
    - 当 `cover` 启用且 `note` 为非 `hold`, 且 `note` 纵坐标小于 `0` 时, 不渲染。
    - 当 `cover` 启用且 `note` 为 `hold` 时, 且 `hold` 尾部纵坐标小于 `0` 时, 不渲染。

    对于使用 `pec` 谱面转换的 `rpe` 谱面文件:
    - 当 `cover` 启用且 `note` 纵坐标小于 `0` 时, 不渲染。

- `numOfNotes`

    `int` 类型, 表示判定线上的 `note` 数量。

    渲染不使用。

- `zOrder`

    `int` 类型, 表示判定线的 `z` 轴顺序。

    使用升序排列, 应使用具有[稳定性](https://baike.baidu.com/item/排序算法稳定性/9763250)的排序算法。

    渲染时先渲染 `zOrder` 较小的判定线。

- `eventLayers`

    `list[typing.Optional[dict[str, list]]]` 类型, 表示判定线上的事件层。

    当一个层级为 `None`, 表示该层级没有事件。

    示例:

    ```python
    {
        "eventLayers": [
            {
                "speedEvents": [],
                "moveXEvents": [],
                "moveYEvents": [],
                "rotateEvents": [],
                "alphaEvents": []
            },
            ..., ..., None, None
        ]
    }
    ```

    对于某一时刻的事件值, 为所有有效事件层的数值之和。

    更多的细节下文会解释。

    <details>
      <summary>你知道的太多了！</summary>

    一般来说, `eventLayers` 的长度为 `5`。

    注意！这并不是规范, 仅仅是 `Re:PhiEdit` 这么做。
    </details>

- `extended`

    `typing.Optional[dict[str, list]]` 类型, 一般来说这里存在一个 `inclineEvents` 的垫底事件。

    这里的事件为可选的, 可就是可以不存在。

    更多的细节下文会解释。

    例如:

    ```json
    {
        "extended": {
            "inclineEvents": [],
            "scaleXEvents": [],
            "scaleYEvents": [],
            "colorEvents": [],
            "textEvents": [],
            "gifEvents": []
        }
    }
    ```

- `notes`

    `list[dict]` 类型, 表示判定线上的 `note`。

    更多的细节下文会解释。

我们定义缓动模块 `rpe_easing`, 函数 `geteasing_func, createBezierFunction, createCuttingEasingFunction` 和 类型 `LineEvent`:

<details>
  <summary>展开</summary>
  
  ```python
  # rpe_easing.py
  
  import math
  import typing
  
  ease_funcs: list[typing.Callable[[float], float]] = [
      lambda t: t, # linear - 1
      lambda t: math.sin((t * math.pi) / 2), # out sine - 2
      lambda t: 1 - math.cos((t * math.pi) / 2), # in sine - 3
      lambda t: 1 - (1 - t) * (1 - t), # out quad - 4
      lambda t: t ** 2, # in quad - 5
      lambda t: -(math.cos(math.pi * t) - 1) / 2, # io sine - 6
      lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 7
      lambda t: 1 - (1 - t) ** 3, # out cubic - 8
      lambda t: t ** 3, # in cubic - 9
      lambda t: 1 - (1 - t) ** 4, # out quart - 10
      lambda t: t ** 4, # in quart - 11
      lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 12
      lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 13
      lambda t: 1 - (1 - t) ** 5, # out quint - 14
      lambda t: t ** 5, # in quint - 15
      lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t), # out expo - 16
      lambda t: 0 if t == 0 else 2 ** (10 * t - 10), # in expo - 17
      lambda t: (1 - (t - 1) ** 2) ** 0.5, # out circ - 18
      lambda t: 1 - (1 - t ** 2) ** 0.5, # in circ - 19
      lambda t: 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2), # out back - 20
      lambda t: 2.70158 * (t ** 3) - 1.70158 * (t ** 2), # in back - 21
      lambda t: (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2, # io circ - 22
      lambda t: ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2, # io back - 23
      lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1), # out elastic - 24
      lambda t: 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3))), # in elastic - 25
      lambda t: 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375))), # out bounce - 26
      lambda t: 1 - (7.5625 * ((1 - t) ** 2) if ((1 - t) < 1 / 2.75) else (7.5625 * ((1 - t) - (1.5 / 2.75)) * ((1 - t) - (1.5 / 2.75)) + 0.75 if ((1 - t) < 2 / 2.75) else (7.5625 * ((1 - t) - (2.25 / 2.75)) * ((1 - t) - (2.25 / 2.75)) + 0.9375 if ((1 - t) < 2.5 / 2.75) else (7.5625 * ((1 - t) - (2.625 / 2.75)) * ((1 - t) - (2.625 / 2.75)) + 0.984375)))), # in bounce - 27
      lambda t: (1 - (7.5625 * ((1 - 2 * t) ** 2) if ((1 - 2 * t) < 1 / 2.75) else (7.5625 * ((1 - 2 * t) - (1.5 / 2.75)) * ((1 - 2 * t) - (1.5 / 2.75)) + 0.75 if ((1 - 2 * t) < 2 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.25 / 2.75)) * ((1 - 2 * t) - (2.25 / 2.75)) + 0.9375 if ((1 - 2 * t) < 2.5 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.625 / 2.75)) * ((1 - 2 * t) - (2.625 / 2.75)) + 0.984375))))) / 2 if t < 0.5 else (1 +(7.5625 * ((2 * t - 1) ** 2) if ((2 * t - 1) < 1 / 2.75) else (7.5625 * ((2 * t - 1) - (1.5 / 2.75)) * ((2 * t - 1) - (1.5 / 2.75)) + 0.75 if ((2 * t - 1) < 2 / 2.75) else (7.5625 * ((2 * t - 1) - (2.25 / 2.75)) * ((2 * t - 1) - (2.25 / 2.75)) + 0.9375 if ((2 * t - 1) < 2.5 / 2.75) else (7.5625 * ((2 * t - 1) - (2.625 / 2.75)) * ((2 * t - 1) - (2.625 / 2.75)) + 0.984375))))) / 2, # io bounce - 28
      lambda t: 0 if t == 0 else (1 if t == 0 else (-2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 + 1) # io elastic - 29
  ]
  ```
  
  ```python
  def geteasing_func(t: int):
      """通过 easingType 获取缓动函数, 返回值为 typing.Callable[[float], float]。"""
      try:
          if not isinstance(t, int): t = 1
          t = 1 if t < 1 else (len(rpe_easing.ease_funcs) if t > len(rpe_easing.ease_funcs) else t)
          return rpe_easing.ease_funcs[int(t) - 1]
      except Exception as e:
          return rpe_easing.ease_funcs[0]
  
  def createBezierFunction(ps: list[float]) -> typing.Callable[[float], float]:
      """获取贝塞尔曲线函数, 返回值为 typing.Callable[[float], float]。"""
      return lambda t: sum([ps[i] * (1 - t) ** (len(ps) - i - 1) * t ** i for i in range(len(ps))])
  
  def createCuttingEasingFunction(f: typing.Callable[[float], float], l: float, r: float):
      """缓动切割。"""
      if l > r: return lambda t: t
      s, e = f(l), f(r)
      return lambda t: (f(t * (r - l) + l) - s) / (e - s)
  
  @dataclass
  class LineEvent:
      startTime: Beat
      endTime: Beat 
      start: float|str|list[int]
      end: float|str|list[int]
      easingType: int = 1
      easingLeft: float = 0.0
      easingRight: float = 1.0
  
      def __post_init__(self):
          self.easingFunc = geteasing_func(self.easingType) if not self.bezier else createBezierFunction(self.bezierPoints)
          self.easingLeft = max(0.0, min(1.0, self.easingLeft))
          self.easingRight = max(0.0, min(1.0, self.easingRight))
          
          if self.easingLeft != 0.0 or self.easingRight != 1.0:
              self.easingFunc = createCuttingEasingFunction(self.easingFunc, self.easingLeft, self.easingRight)
  ```

</details>

`rpe` 的坐标系位于屏幕中心, 向右为 x 轴正方向, 向上为 y 轴正方向。

x 轴单位为 `W / 1350`, y 轴单位为 `H / 900`。

一般的, 单个 `LineEvent` 的 `start` 和 `end` 均为同种类型, 可以是 `float`、`str` 或 `list[int]`。 ~~这里示例代码好像没有做好类型标注~~

一般来说, 假如缓动函数为 `f: typing.Callable[[float], float]`, 则 `f(0.0) = 0.0`, `f(1.0) = 1.0`。

`eventLayers` 的单个元素结构:

- `speedEvents`

    `list[dict]` 类型, 表示判定线上的 `speed` 事件。

  - `startTime` `Beat` 类型, 表示 `speed` 事件开始的时间。
  - `endTime` `Beat` 类型, 表示 `speed` 事件结束的时间。
  - `start` `float` 类型, 表示 `speed` 事件开始时的速度。
  - `end` `float` 类型, 表示 `speed` 事件结束时的速度。
  - `easingType` `typing.Literal[1]` 类型, 表示 `speed` 事件的缓动。

      其实就是 `linear`。

    单位为 `120` 个 y 轴单位 `/ s`，即 `(H / 900 * 120) / s = (H / 7.5) / s`。

    让我们来计算一个 `speed` 事件吧！

    例如当前 `bpm` 为 `120`，当前时间为 `1.5 beat`，`speed` 事件为 (默认键省去):

    ```json
    {
        "startTime": [0, 0, 1],
        "endTime": [5, 1, 2],
        "start": 10.0,
        "end": 25.0,
        "easingType": 1
    }
    ```

    那么当前我们来计算这个 `speed` 事件流过的距离:

    ```python
    eventTime = event.endTime.value - event.startTime.value
    eventProgress = (1.5 - event.startTime.value) / eventTime

    startSpeed = event.start
    nowSpeed = event.start + (event.end - event.start) * eventProgress

    timeSecond = beat2sec(1.5, 1.0, [BpmEvent(
        bpm = 120,
        startTime = Beat(0, 0, 1)
    )])

    result = (nowSpeed + startSpeed) * timeSecond / 2
    result *= H / 900 * 120
    ```
