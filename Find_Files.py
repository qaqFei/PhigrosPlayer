from os import listdir
from os.path import isfile

def Get_All_Files(path:str) -> list[str]:
    if path[-1] == "/" or path[:-1] == "\\":
        path = path[:-1]
    path = path.replace("/", "\\")
    files = []
    for item in listdir(path):
        if isfile(f"{path}\\{item}"):
            files.append(f"{path}\\{item}")
        else:
            files += Get_All_Files(f"{path}\\{item}")
    return files