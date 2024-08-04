from sys import argv
from json import load

from pydub import AudioSegment

import Const
import Chart_Functions_Rpe

NoteClickAudios = {
    Const.Note.TAP: AudioSegment.from_file("./Resources/Note_Click_Audio/Tap.wav"),
    Const.Note.DRAG: AudioSegment.from_file("./Resources/Note_Click_Audio/Drag.wav"),
    Const.Note.HOLD: AudioSegment.from_file("./Resources/Note_Click_Audio/Hold.wav"),
    Const.Note.FLICK: AudioSegment.from_file("./Resources/Note_Click_Audio/Flick.wav")
}

with open(argv[1], "r", encoding="utf-8") as f:
    Chart = load(f)

if "META" in Chart and "formatVersion" not in Chart:
    rpeobj = Chart_Functions_Rpe.Load_Chart_Object(Chart)
    Chart = {
        "formatVersion": 3,
        "offset": rpeobj.META.offset / 1000,
        "judgeLineList": [
            {
                "bpm": 1.875,
                "notesAbove": [
                    {
                        "time": rpeobj.beat2sec(note.startTime.value),
                        "type": note.phitype
                    }
                    for note in line.notes if not note.isFake
                ],
                "notesBelow": []
            }
            for line in rpeobj.JudgeLineList
        ]
    }

ChartAudio:AudioSegment = AudioSegment.from_file(argv[2])
ChartAudio_Length = ChartAudio.duration_seconds
ChartAudio_Split_Audio_Block_Length = 3500 #ms
ChartAudio_Split_Length = int(ChartAudio_Length / (ChartAudio_Split_Audio_Block_Length / 1000)) + 1
ChartAudio_Split_Audio_List = [AudioSegment.silent(ChartAudio_Split_Audio_Block_Length + 500) for _ in [None] * ChartAudio_Split_Length]
JudgeLine_cut = 0

for JudgeLine in Chart["judgeLineList"]:
    t_dw = 1.875 / JudgeLine["bpm"]
    Note_cut = 0
    for note in JudgeLine["notesBelow"] + JudgeLine["notesAbove"]:
        t = note["time"] * t_dw
        t_index = int(t / (ChartAudio_Split_Audio_Block_Length / 1000))
        t %= ChartAudio_Split_Audio_Block_Length / 1000
        seg:AudioSegment = ChartAudio_Split_Audio_List[t_index]
        ChartAudio_Split_Audio_List[t_index] = seg.overlay(NoteClickAudios[note["type"]], t * 1000)
        print(f"Process Note: {JudgeLine_cut}+{Note_cut}")
        Note_cut += 1
    JudgeLine_cut += 1

print("Merge...")
for i,seg in enumerate(ChartAudio_Split_Audio_List):
    ChartAudio = ChartAudio.overlay(seg, i * ChartAudio_Split_Audio_Block_Length + Chart["offset"] * 1000)

ChartAudio.export(argv[3])

print("Done.")