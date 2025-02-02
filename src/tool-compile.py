from zipfile import ZipFile
from threading import Thread
from os import system, mkdir, listdir
from os.path import isfile
from sys import argv
from shutil import copy, copytree

system("cls")

if "-y" not in argv:
    if input("Sure? (y/n) ").lower() not in ("yes", "y"):
        raise SystemExit

def compile(file:str, hideconsole:bool):
    system(f"{pyi_makespec} \"{file}\" -i icon.ico {"-w" if hideconsole and not debug else ""}")
    spec = f"{file.replace('.py', '')}.spec"
    with open(spec, "r", encoding="utf-8") as f:
        spec_data = f.read()
    with open(spec, "w", encoding="utf-8") as f:
        f.write(extend + spec_data)
    system(f"{pyinstaller} \"{spec}\"")
    system(f"del {file.replace(".py", ".spec")}")

debug = "--debug" in argv
compile_files = [
    ("main.py", False),
    ("gui_launcher.py", False),
    ("phigros.py", False),
    *(map(lambda x: (x, False), filter(lambda x: x.startswith("tool-") and x.endswith(".py") and x != "tool-compile.py", listdir())))
]
res_files = [
    "_internal",
    "web_canvas.html",
    "ecwv_installer.exe",
    "resources",
    "icon.ico",
    "openh264-1.8.0-win64.dll"
]
extend = open("_compile_pyiextend.py", "r", encoding="utf-8").read()

system("python -m venv compile_venv")
py = ".\\compile_venv\\Scripts\\python.exe"

system(f"{py} -m pip install --upgrade pip")
system(f"{py} -m pip install -r .\\requirements.txt")
system(f"{py} -m pip install pyinstaller")

pyinstaller = ".\\compile_venv\\Scripts\\pyinstaller.exe"
pyi_makespec = ".\\compile_venv\\Scripts\\pyi-makespec.exe"
ts: list[Thread] = []

for file, hideconsole in compile_files:
    ts.append(Thread(target=compile, args=(file, hideconsole)))

for t in ts: t.start()
for t in ts: t.join()

for file, _ in compile_files:
    system(f"xcopy \".\\dist\\{file.replace(".py", "")}\\*\" .\\ /c /q /e /y")

system("rmdir .\\compile_venv /s /q")
system("rmdir .\\build /s /q")
system("rmdir .\\dist /s /q")

if "--zip" in argv:
    _copy = lambda src, tar: copy(src, tar) if isfile(src) else copytree(src, f"{tar}\\{src}")
    try: mkdir(".\\compile_result")
    except FileExistsError: pass
    for i, _ in compile_files:
        _copy(i.replace(".py", ".exe"), ".\\compile_result")
    for i in res_files:
        _copy(i, ".\\compile_result")
    with ZipFile("compile_result.zip", "w") as zipf:
        for f in listdir("compile_result"):
            zipf.write(f"compile_result/{f}", arcname=f)

print("\nCompile complete!")
system("pause")