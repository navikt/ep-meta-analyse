#!/usr/bin/env python3

import os
from datetime import timedelta
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


report_part("Highlight: Risky changes", changes, lambda change: 3 <= int(change["risk"]) <= 5)
report_part("Changes with unknown intention", changes, lambda change: change["intention"] in {"*"})
report_part("Feature and bugfix changes", changes, lambda change: change["intention"] in {"F", "B"})
report_part("Refactoring, test and documentation changes", changes, lambda change: change["intention"] in {"R", "T", "D"})
report_part("Environment changes", changes, lambda change: change["intention"] in {"E"})
report_part("Dependency updates", changes, lambda change: change["intention"] in {"U"})
report_part("Minor changes", changes, lambda change: change["intention"] in {"A", "P"})
