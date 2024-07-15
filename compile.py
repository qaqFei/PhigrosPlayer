from threading import Thread
from os import system
from sys import argv

if input("Sure? (y/n) ").lower() not in ("yes", "y"):
    raise SystemExit

def compile(file:str, hideconsole:bool):
    system(f"{pyinstaller} \"{file}\" -i icon.ico {"-w" if hideconsole and not debug else ""}")
    system(f"del {file.replace(".py", ".spec")}")

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