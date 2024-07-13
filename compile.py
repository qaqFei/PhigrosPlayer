from os import system, listdir
from os.path import isfile
from sys import argv

debug = "--debug" in argv
compile_files = [
    ("Main.py", True),
    ("GUI_Launcher.py", True),
    ("rpe2phi.py", False),
    ("ProcessChartAudio.py", False),
]

system("python -m venv compile_venv")
py = ".\\compile_venv\\Scripts\\python.exe"

system(f"{py} -m pip install --upgrade pip")
system(f"{py} -m pip install -r requirements.txt")
system(f"{py} -m pip install pyinstaller")
pyinstaller = ".\\compile_venv\\Scripts\\pyinstaller.exe"

pyfiles = [i for i in listdir(".") if i.endswith(".py") and isfile(i)]
importlines = set()
for file in pyfiles:
    try:
        with open(file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if line.startswith("import ") or line.startswith("from "):
                    if "__future__" not in line:
                        importlines.add(line)
    except Exception:
        pass
with open("_import_packs.py", "w", encoding="utf-8") as f:
    f.writelines(importlines)
    
system(f"{pyinstaller} _import_packs.py")
system(f"del _import_packs.spec")
system(f"xcopy .\\dist\\_import_packs\\_internal\\* .\\_internal\\ /c /q /e /y")

for file, hideconsole in compile_files:
    system(f"{pyinstaller} \"{file}\" -i icon.ico {"-w" if hideconsole and not debug else ""}")
    name = file.replace(".py", "")
    system(f"xcopy \".\\dist\\{name}\\{name}.exe\" .\\ /c /q /e /y")
    system(f"del {file.replace(".py", ".spec")}")

system("rmdir .\\compile_venv /s /q")
system("rmdir .\\build /s /q")
system("rmdir .\\dist /s /q")
system("del _import_packs.py")
system("pause")