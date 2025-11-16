#!/usr/bin/env python3

import re
import os
from datetime import timedelta
from lib.commit_data import intentions
from lib.commit_data import text_risk, gather_changes_from_subprojects

changes = gather_changes_from_subprojects(os.getcwd() + '/..', timedelta(days=7, hours=10))

changes.sort(key=lambda change: change['intention'])
changes.sort(key=lambda change: change['risk'], reverse=True)
changes.sort(key=lambda change: change['branch_type'])
changes.sort(key=lambda change: change['timestamp'])
changes.sort(key=lambda change: change['module'])
changes.sort(key=lambda change: change['type'])

def report_part(description, changes, filter_rule):
    print("*** " + description + " *** ")
    print()
    for change in filter(filter_rule, changes):
        print(f'{change["timestamp"].strftime("%d-%m-%Y %H:%M")} {change["module"].rjust(22," ")} * {change["branch_type"].rjust(1," ")} * - {change["message"]}  ({text_risk(change["risk"])})')
    print()

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

intention_keys = {k for k in intentions if k != "*"}
all_intention_keys = intention_keys | {k.lower() for k in intention_keys}
intention_pattern = re.compile(rf'^([{ "".join(all_intention_keys)}])([ !\-])')

def not_revert(change):
    return "message" in change and not change["message"].lower().startswith("revert")

risky_changes = [
    c for c in changes
    if 3 <= int(c.get("risk", 0)) <= 5
    and intention_pattern.match(c.get("message", ""))
    and not_revert(c)
]

unknown_changes = [
    c for c in changes
    if not intention_pattern.match(c.get("message", ""))
    and not_revert(c)
]

report_part("Highlight: Risky changes", risky_changes, lambda change: True)
report_part("Changes with unknown intention", unknown_changes, lambda change: True)
report_part("Feature and bugfix changes", changes, lambda change: change["intention"] in {"F", "B"})
report_part("Refactoring, test and documentation changes", changes, lambda change: change["intention"] in {"R", "T", "D"})
report_part("Environment changes", changes, lambda change: change["intention"] in {"E"})
report_part("Dependency updates", changes, lambda change: change["intention"] in {"U"})
report_part("Minor changes", changes, lambda change: change["intention"] in {"A", "P"})
