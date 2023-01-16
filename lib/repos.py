import re
import subprocess


def paths_from_ls_cmd(folder):
    subfolders_with_git_cmd = subprocess.run(["sh", "-c", f"ls --color=never -d */.git"], stdout=subprocess.PIPE, text=True, cwd=folder)
    if subfolders_with_git_cmd.returncode != 0:
        exit(subfolders_with_git_cmd.returncode)
    sub_folders_with_git = subfolders_with_git_cmd.stdout.split('\n')
    root_project_folder = "."
    return [root_project_folder] + [re.sub('/.git', '', folder) for folder in sub_folders_with_git if folder != ""]


def projects_info(folder):
    result = []
    for path in paths_from_ls_cmd(folder):
        result += [{
            "path": path,
            "module": re.sub("^\.$", "meta", re.sub("eessi-pensjon-", "", path)),
            "type": type_from_path(path)
        }]
    return result


def type_from_path(project):
    if project.startswith(".") or project.startswith("ep-meta-"):
        return "meta"
    if project.startswith("eessi-pensjon-") and project != "eessi-pensjon-ui":
        return "app"
    return "library"
