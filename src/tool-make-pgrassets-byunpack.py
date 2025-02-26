import fix_workpath as _

import json
from os import mkdir
from sys import argv

if len(argv) < 3:
    print("Usage: tool-make-pgrassets-byunpack <unpack-result> <output-dir>")
    raise SystemExit

unpack_result = argv[1]
output_dir = argv[2]

mkdir(output_dir)

pgr_chapters_info = json.load(open("./resources/pgr_chapters.json", "r", encoding="utf-8"))
