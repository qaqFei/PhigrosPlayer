from sys import argv
from json import load,dumps

if len(argv) < 4:
    raise SystemExit

with open(argv[1],"r") as f:
    chart = load(f)

for filename in argv[2:-1]:
    with open(filename,"r") as f:
        chart["judgeLineList"] += load(f)["judgeLineList"]

with open(argv[-1],"w") as f:
    f.write(dumps(chart))