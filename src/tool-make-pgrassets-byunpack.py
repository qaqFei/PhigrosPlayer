import fix_workpath as _

import json
from os import mkdir
from os.path import isdir
from sys import argv
from shutil import rmtree

if len(argv) < 3:
    print("Usage: tool-make-pgrassets-byunpack <unpack-result> <output-dir>")
    raise SystemExit

unpack_result = argv[1]
output_dir = argv[2]

try: rmtree(output_dir)
except FileNotFoundError: pass
try: mkdir(output_dir)
except FileExistsError: pass

if not isdir(f"{unpack_result}/other_res"):
    print("fatal: unpack result need other res (--need-other-res in unpack).")
    raise SystemExit

pgr_chapters_info = json.load(open("./resources/pgr_chapters.json", "r", encoding="utf-8"))
upk_info = json.load(open(f"{unpack_result}/info.json", "r", encoding="utf-8"))
unp_all_ids = [i["songIdBak"] for i in upk_info]

for i in pgr_chapters_info:
    if i["split"] not in unp_all_ids:
        print(f"fatal: cannot find {i["split"]} in unpack result, please check your version.")
        raise SystemExit

class splitSongManager:
    def __init__(self, songs: list[dict]):
        self.songs = songs
    
    def get_songs(self, point: str, count: int, jumps: list[str]):
        jumps = jumps.copy()
        jumps.insert(0, point)
        result = []
        
        for i, point in enumerate(jumps):
            if i != len(jumps) - 1:
                result.extend([i for i in songs if i["songIdBak"] == point])
                count -= 1
            else:
                i = self.songs.index([i for i in self.songs if i["songIdBak"] == point][0])
                result.extend(self.songs[i:i + count])

        for i in self.songs.copy():
            if i["songIdBak"] in [j["songIdBak"] for j in result]:
                self.songs.remove(i)

        return result

ssm = splitSongManager(upk_info)
chapters = {"chapters": []}

for ciindex, cinfo in enumerate(pgr_chapters_info):
    songs = ssm.get_songs(cinfo["split"], cinfo["count"], cinfo.get("jumps", []))

    if cinfo.get("reverse", False):
        songs.reverse()
    
    