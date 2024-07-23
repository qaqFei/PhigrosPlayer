from os import system

def git(cmd):
    system(f"git {cmd} > gitout.txt")
    return open("gitout.txt", "r", encoding="utf-8").read()

f = open("ChangeLogs_.md", "w", encoding="utf-8")
f.write("# PhigrosPlayer Github Commit 修改日志\n\n")

logs = git("log").split("\n")
hashIDs = [i[7:] for i in logs if i.startswith("commit ") and len(i) == 47][::-1]

for index, hashID in enumerate(hashIDs):
    print(hashID)
    commit_time = git(f"log {hashID} -1 --pretty=format:\"%cd\"").split("\n")[0]
    commit_cn = git(f"log {hashID} -1 --pretty=format:\"%cn\"").split("\n")[0]
    
    f.write(f"## Commit {index + 1} - `{hashID}`\n")
    f.write(f"- 时间: `{commit_time}`\n")
    f.write(f"- 提交者: `{commit_cn}`\n")
    f.write(f"- Commit 链接: [Click Me](https://github.com/qaqFei/PhigrosPlayer/commit/{hashID})\n")
    f.write(f"- 描述:\n    - null\n\n")
    
f.close()
system("del gitout.txt")