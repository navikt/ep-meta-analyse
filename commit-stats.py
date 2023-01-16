#!/usr/bin/env python3

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from lib.commit_data import gather_changes_from_subprojects
import csv

startdate = datetime(2021, 1, 1)

changes = gather_changes_from_subprojects(os.getcwd(), datetime.now() - startdate)

filename = "analysis/commit-stats.csv"


def convert(value):
    if isinstance(value, datetime):
        return convert_datetime(value)

    return value


def convert_datetime(value):
    """Konverterer datetime med TZ til streng med europeisk lokal tid"""

    localtime = value.astimezone(ZoneInfo('Europe/Berlin'))
    return localtime.strftime("%Y-%m-%d %H:%M:%S")


with open(filename, 'w', encoding="UTF-16") as csvfile:  # UTF-16 because Excel is stupid
    writer = csv.writer(csvfile, delimiter=';', dialect='excel')
    columns = changes[0].keys()
    writer.writerow(columns)
    for line in changes:
        row = []
        for column in columns:
            row += [convert(line[column])]
        writer.writerow(row)
