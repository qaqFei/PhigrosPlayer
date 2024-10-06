from sys import argv
from PIL import Image
import json

import cv2

if len(argv) < 3:
    print("video2rpe.py <input video> <output rpe chart>")
    raise SystemExit


w, h = 64, 36
video = cv2.VideoCapture(argv[1])
vwidth, vheight = int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
vp = vwidth / vheight
if vp >= w / h:
    vheight = int(w / vp)
    vwidth = w
else:
    vwidth = int(h * vp)
    vheight = h

getLine = lambda x, y, o: {"Group":0,"Name":"Untitled","Texture":"line.png","alphaControl":[{"alpha":1.0,"easing":1,"x":0.0},{"alpha":1.0,"easing":1,"x":9999999.0}],"bpmfactor":1.0,"eventLayers":[{"alphaEvents":[{"bezier":0,"bezierPoints":[0.0,0.0,0.0,0.0],"easingLeft":0.0,"easingRight":1.0,"easingType":1,"end":255,"endTime":[1,0,1],"linkgroup":0,"start":255,"startTime":[0,0,1]}],"moveXEvents":[{"bezier":0,"bezierPoints":[0.0,0.0,0.0,0.0],"easingLeft":0.0,"easingRight":1.0,"easingType":1,"end":x,"endTime":[1,0,1],"linkgroup":0,"start":x,"startTime":[0,0,1]}],"moveYEvents":[{"bezier":0,"bezierPoints":[0.0,0.0,0.0,0.0],"easingLeft":0.0,"easingRight":1.0,"easingType":1,"end":y,"endTime":[1,0,1],"linkgroup":0,"start":y,"startTime":[0,0,1]}],"rotateEvents":[{"bezier":0,"bezierPoints":[0.0,0.0,0.0,0.0],"easingLeft":0.0,"easingRight":1.0,"easingType":1,"end":0.0,"endTime":[1,0,1],"linkgroup":0,"start":0.0,"startTime":[0,0,1]}],"speedEvents":[]}],"extended":{"inclineEvents":[{"bezier":0,"bezierPoints":[0.0,0.0,0.0,0.0],"easingLeft":0.0,"easingRight":1.0,"easingType":0,"end":0.0,"endTime":[1,0,1],"linkgroup":0,"start":0.0,"startTime":[0,0,1]}], "textEvents":[{"bezier":0,"bezierPoints":[0.0,0.0,0.0,0.0],"easingLeft":0.0,"easingRight":1.0,"easingType":0,"end":"■","endTime":[1,0,1],"linkgroup":0,"start":"■","startTime":[0,0,1]}], "colorEvents":[]},"father":-1,"isCover":1,"notes":[],"numOfNotes":0,"posControl":[{"easing":1,"pos":1.0,"x":0.0},{"easing":1,"pos":1.0,"x":9999999.0}],"sizeControl":[{"easing":1,"size":1.0,"x":0.0},{"easing":1,"size":1.0,"x":9999999.0}],"skewControl":[{"easing":1,"skew":0.0,"x":0.0},{"easing":1,"skew":0.0,"x":9999999.0}],"yControl":[{"easing":1,"x":0.0,"y":1.0},{"easing":1,"x":9999999.0,"y":1.0}],"zOrder":o}
tpos = lambda x, y: (1350 * (x - 1 / 2), 900 * (1 / 2 - y))
getindex = lambda x, y: x * h + y

rpeChart = {
    "BPMList": [{"bpm": 60 * int(video.get(cv2.CAP_PROP_FPS)), "startTime": [0, 0, 1]}],
    "META": {"RPEVersion": 140, "background": "bg.png", "charter": "", "composer": "", "id": "0", "level": "", "name": "", "offset": 0, "song": "song.mp3"},
    "judgeLineGroup": ["Default"],
    "judgeLineList": []
}

for x in range(w):
    for y in range(h):
        rpeChart["judgeLineList"].append(getLine(*tpos(x / w, y / h), getindex(x, y)))

fcut = 0
while True:
    ret, frame = video.read()
    if not ret: break
    pilFrame = Image.fromarray(frame[:, :, ::-1])
    newPilFrame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    newPilFrame.paste(pilFrame.resize((vwidth, vheight)), (int((w - vwidth) / 2), int((h - vheight) / 2)))
    for x in range(w):
        for y in range(h):
            r, g, b, a = newPilFrame.getpixel((x, y))
            if a != 0:
                line = rpeChart["judgeLineList"][getindex(x, y)]
                line["extended"]["colorEvents"].append({
                    "bezier": 0,
                    "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                    "easingLeft": 0.0,
                    "easingRight": 1.0,
                    "easingType": 1,
                    "end": [r, g, b],
                    "endTime": [fcut + 1, 0, 1],
                    "linkgroup": 0,
                    "start": [r, g, b],
                    "startTime": [fcut, 0, 1]
                })
    fcut += 1
    print(fcut)

video.release()
with open(argv[2], "w", encoding="utf-8") as f:
    json.dump(rpeChart, f)