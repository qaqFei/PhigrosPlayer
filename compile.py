from os import system
from sys import argv

debug = "--debug" in argv
compile_files = [
    "Main.py",
    "rpe2phi.py",
    "ProcessChartAudio.py"
]

system("python -m venv compile_venv")
py = ".\\compile_venv\\Scripts\\python.exe"

system(f"{py} -m pip install --upgrade pip")
system(f"{py} -m pip install -r requirements.txt")
system(f"{py} -m pip install pyinstaller")
pyinstaller = ".\\compile_venv\\Scripts\\pyinstaller.exe"

for file in compile_files:
    system(f"{pyinstaller} \"{file}\" -i icon.ico {"-w" if not debug else ""}")
    name = file.replace(".py", "")
    system(f"xcopy \".\\dist\\{name}\\*\" .\\ /c /q /e /y")
    system(f"del {file.replace(".py", ".spec")}")

system("rmdir .\\compile_venv /s /q")
system("rmdir .\\build /s /q")
system("rmdir .\\dist /s /q")
system("pause")