import json
from sys import argv

import mido
import mido.messages
import mido.midifiles

import const

if len(argv) < 3:
    print("Usage: tool-midi2phi <midiFile> <outputFile>")
    raise SystemExit

def fixre_readmsg(infile, status_byte, peek_data, delta, clip=False):
    try: spec = mido.messages.SPEC_BY_STATUS[status_byte]
    except LookupError as le: raise OSError(f"undefined status byte 0x{status_byte:02x}") from le
    data_bytes = peek_data + mido.midifiles.midifiles.read_bytes(infile, spec["length"] - 1 - len(peek_data))
    if clip: data_bytes = [byte if byte < 127 else 127 for byte in data_bytes]
    else:
        for i, byte in enumerate(data_bytes):
            if byte > 127: data_bytes[i] = 127
    return mido.messages.messages.Message.from_bytes([status_byte] + data_bytes, time=delta)
mido.midifiles.midifiles.read_message = fixre_readmsg

mid = mido.MidiFile(argv[1])

def pcs():
    onmsgs = []
    
    t = 0.0
    for msg in mid:
        t += msg.time
        if msg.type == "note_on":
            onmsgs.append((t, msg.note))
    
    onmsgs.sort(key = lambda x: x[0])
    min_note, max_note = min(onmsgs, key=lambda x: x[1])[1], max(onmsgs, key=lambda x: x[1])[1]
    
    last = (float("nan"), float("nan"))
    for t, n in onmsgs:
        r = t, (n + 1 - (max_note - min_note) / 2 - min_note) / (max_note - min_note) / const.PGR_UW * 0.8
        if r != last:
            yield r
        last = r

result = {
    "formatVersion": 3,
    "offset": 0.0,
    "judgeLineList": [
        {
            "bpm": 1.875,
            "notesAbove": [
                {
                    "type": 1,
                    "time": t,
                    "holdTime": 0.0,
                    "positionX": x,
                    "speed": 1.0,
                    "floorPosition": 2.2 * t
                }
                for t, x in pcs()
            ],
            "notesBelow": [],
            "speedEvents": [
                {
                    "startTime": 0.0,
                    "value": 2.2,
                    "endTime": 999999.0
                }
            ],
            "judgeLineMoveEvents": [
                {
                    "startTime": -999999.0,
                    "endTime": 999999.0,
                    "start": 0.5,
                    "end": 0.5,
                    "start2": 0.2,
                    "end2": 0.2
                }
            ],
            "judgeLineRotateEvents": [
                {
                    "startTime": -999999.0,
                    "endTime": 999999.0,
                    "start": 0.0,
                    "end": 0.0
                }
            ],
            "judgeLineDisappearEvents": [
                {
                    "startTime": -999999.0,
                    "endTime": 999999.0,
                    "start": 1.0,
                    "end": 1.0
                }
            ]
        }
    ]
}

with open(argv[2], "w", encoding="utf-8") as f:
    json.dump(result, f)