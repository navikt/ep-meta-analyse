import subprocess
from datetime import datetime

from .repos import projects_info

risks = {
    '0': "no risk",
    '1': "known safe",
    '2': "validated",
    '3': "risky",
    '4': "(probably) broken",
    '5': "unknown risk",
}

intentions = {
    'F': "feature",
    'R': "refactoring",
    'T': "tests only",
    'B': "bugfix",
    'E': "environment",
    'D': "documentation",
    'P': "process (build/deploy)",
    'A': "automated formatting etc",
    'U': "dependency update",
    '*': "unknown"
}


def intention_from_message(message):
    if message.startswith("[Release Plugin]"):
        return "P"
    if message.lower().startswith("e oppgraderer"):
        return "U"
    if message.startswith("Revert \""):
        return intention_from_message(message[len("Revert \""):])
    if (len(message) >= 3 and message[1:3] in (" -", "!!", "**")) or (len(message) >= 2 and message[1] == " "):  # last condition handles old messages
        return message[0].upper() if message[0].upper() in intentions.keys() else "*"
    return "*"


def text_intention(intention):
    return intentions.get(intention.upper(), "unknown")


def text_risk(risk):
    return risks.get(risk, "unknown")


def risk_from_message(message):
    if message.startswith("[Release Plugin]"):
        return "0"
    if message.startswith("Revert \""):
        return risk_from_message(message[len("Revert \""):])
    if (len(message) >= 3 and message[1:3] not in (" -", "!!", "**")) and (len(message) > 2 and message[1] != " "):  # last condition handles old messages
        return "5"
    if message[0].islower():
        return "1"
    if message[1:3] == "**":
        return "4"
    if message[1:3] == "!!":
        return "3"
    if message[1:3] == " -":
        return "2"
    if message[1] == " ": # handle old commits
        return "2"
    else:
        return "5"


def gather_changes_from_subprojects(root_dir, duration):
    hours, remainder = divmod(duration.total_seconds(), 3600)
    report_period = "%d hours" % (hours + (1 if remainder > 0 else 0))

    changes = []
    for project_info in projects_info(root_dir):
        for commit in project_commits(root_dir, project_info, report_period):
            (timestamp, hash, subject) = tuple(commit)
            changes += [{
                "repo": project_info["path"],
                "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S %z"),
                "module": project_info["module"],
                "type": project_info["type"],
                "hash": hash,
                "message": subject,
                "intention": intention_from_message(subject),
                "risk": risk_from_message(subject)
            }]
    return changes


def project_commits(root_dir, project_info, report_period):
    commit_format_string = f"%ci€%h€%s"
    path = root_dir + '/' + project_info["path"]
    project_changes_cmd = subprocess.run(["sh", "-c",
                                          f"git fetch >/dev/null && git log origin/HEAD --format='{commit_format_string}' --since='{report_period}'"],
                                         cwd=path, stdout=subprocess.PIPE, text=True)
    commit_lines = project_changes_cmd.stdout.split('\n')
    return [line.split("€") for line in commit_lines if line != ""]
