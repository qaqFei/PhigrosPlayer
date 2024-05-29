from sys import argv
from json import load,dumps

if len(argv) < 4:
    raise SystemExit

with open(argv[1],"r") as f:
    chart = load(f)

with open(argv[2],"r") as f:
    chart["judgeLineList"] += load(f)["judgeLineList"]

with open(argv[3],"w") as f:
    f.write(dumps(chart))