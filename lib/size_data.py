import datetime
import os
import time
from subprocess import Popen, PIPE
from dateutil.relativedelta import relativedelta

from .repos import projects_info


def cloc_for(path):
    cloc_command_string = 'cloc --csv --vcs git --exclude-dir=dist,build,gradle --exclude-list-file=.clocignore --exclude-lang=JSON,XML --quiet .'
    cloc_command = Popen(cloc_command_string, shell=True, stdout=PIPE, cwd=path, text=True)
    if cloc_command.returncode:
        exit(cloc_command.returncode)
    result = []
    for line in cloc_command.stdout.readlines():
        result += [line.rstrip()]
    return result[1:-1]  # fjerner header og SUM


def cloc_change(path, from_date, to_date):  # --exclude-list-file=.clocignore fungerer ikke her ser det ut til
    to_commit = Popen(f'git rev-list --before="{to_date}" origin/HEAD | head -n 1', shell=True, stdout=PIPE,
                      cwd=path, text=True).stdout.readline().rstrip('\n')
    if not to_commit:
        return []

    from_commit = Popen(f'git rev-list --before="{from_date}" origin/HEAD | head -n 1', shell=True, stdout=PIPE,
                        cwd=path, text=True).stdout.readline().rstrip()
    if not from_commit:
        from_commit = Popen(f'git rev-list --max-parents=0 origin/HEAD | head -n 1', shell=True, stdout=PIPE,
                            cwd=path, text=True).stdout.readline().rstrip()
    if from_commit == to_commit:
        return []

    cloc_command_string = f'cloc --csv --vcs git --exclude-dir=dist,build,gradle --exclude-lang=JSON,XML --quiet --diff --git {from_commit} {to_commit}'
    cloc_command = Popen(cloc_command_string, shell=True, stdout=PIPE, cwd=path, text=True)
    if cloc_command.returncode:
        exit(cloc_command.returncode)
    time.sleep(2)
    result = []
    for line in cloc_command.stdout.readlines():
        if line.startswith("Nothing to count."):
            break
        result += [line.rstrip()]
    return result[1:]


def size_data(root_dir):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    size_stats = []

    projects = projects_info(root_dir)
    for project in projects:
        cloc_stats = cloc_for(root_dir + '/' + project["path"])
        for row in cloc_stats:
            data = row.split(",")
            size_stats += [{
                "date": today,
                "repo": project["path"],
                "module": project["module"],
                "type": project["type"],
                "files": data[0],
                "language": data[1],
                "blank lines": data[2],
                "comment lines": data[3],
                "code lines": data[4],
            }]

    return size_stats


def change_data(root_dir, tertial):
    from_date = datetime.datetime(year=int(tertial[0:4]), month=int(tertial[5])*4-3, day=1)
    to_date = from_date + relativedelta(months=4)

    change_stats = []

    for project in projects_info(root_dir):
        cloc_stats = cloc_change(root_dir + '/' + project["path"], from_date, to_date)
        for row in cloc_stats:
            data = row.split(",")
            change_stats += [{
                "tertial": tertial,
                "repo": project["path"],
                "module": project["module"],
                "type": project["type"],
                "language": data[0],
                "== files": data[1],
                "!= files": data[2],
                "+ files": data[3],
                "- files": data[4],
                "== blank": data[5],
                "!= blank": data[6],
                "+ blank": data[7],
                "- blank": data[8],
                "== comment": data[9],
                "!= comment": data[10],
                "+ comment": data[11],
                "- comment": data[12],
                "== code": data[13],
                "!= code": data[14],
                "+ code": data[15],
                "- code": data[16],
            }]

    return change_stats
