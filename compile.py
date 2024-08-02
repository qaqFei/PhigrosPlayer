from threading import Thread
from os import system
from sys import argv

system("cls")

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
    ("Main.py", False),
    ("GUI_Launcher.py", True),
    ("ProcessChartAudio.py", False),
    ("OutputVideo.py", False)
]
extend = open("_compile_pyiextend.py", "r", encoding="utf-8").read()

system("python -m venv compile_venv")
py = ".\\compile_venv\\Scripts\\python.exe"

system(f"{py} -m pip install --upgrade pip")
system(f"{py} -m pip install -r requirements.txt")
system(f"{py} -m pip install pyinstaller")
pyinstaller = ".\\compile_venv\\Scripts\\pyinstaller.exe"
pyi_makespec = ".\\compile_venv\\Scripts\\pyi-makespec.exe"
ts:list[Thread] = []

for file, hideconsole in compile_files:
    ts.append(Thread(target=compile, args=(file, hideconsole)))

for t in ts:
    t.start()
for t in ts:
    t.join()

for file, _ in compile_files:
    system(f"xcopy \".\\dist\\{file.replace(".py", "")}\\*\" .\\ /c /q /e /y")

system("rmdir .\\compile_venv /s /q")
system("rmdir .\\build /s /q")
system("rmdir .\\dist /s /q")
print("\nCompile complete!")
system("pause")