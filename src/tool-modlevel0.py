import fix_workpath as _

import json
from sys import argv

import UnityPy
import UnityPy.classes
import UnityPy.files
import UnityPy.streams

if len(argv) < 5:
    print("Usage: tool-modlevel0 <level0> <globalgamemanagers.assets> <info-ftt> <output-dir>")
    raise SystemExit

with open("./resources/pgr_unpack_treetype.json", "r", encoding="utf-8") as f:
    treetype = json.load(f)
    
info_ftt = json.load(open(argv[3], "r", encoding="utf-8"))
        
env = UnityPy.Environment()
env.load_file(argv[2], name="assets/bin/Data/globalgamemanagers.assets")
env.load_file(argv[1])

for obj in env.objects:
    if obj.type.name != "MonoBehaviour": continue
    
    data = obj.read()
    name = data.m_Script.get_obj().read().name
    
    if name == "GameInformation":
        obj.save_typetree(info_ftt, treetype["GameInformation"])
    
env.save(out_path=argv[4])
print("modified.")
