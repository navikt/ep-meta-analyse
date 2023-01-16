#!/usr/bin/env python3

import os
import csv
import datetime
import shutil

from lib.size_data import size_data, change_data

today = datetime.datetime.today().strftime('%Y-%m-%d')
tertial = "2022T3"

size_file_wth_date = f"{os.getcwd()}/analysis/cloc-{today}.csv"
size_file = f"{os.getcwd()}/analysis/cloc.csv"
change_file = f"{os.getcwd()}/analysis/cloc-change-{tertial}.csv"

if os.path.exists(size_file_wth_date):
    os.remove(size_file_wth_date)

with open(size_file_wth_date, 'w', encoding="UTF-16") as csvfile:  # UTF-16 because Excel is stupid
    writer = csv.writer(csvfile, delimiter=';', dialect='excel')
    data = size_data()
    columns = data[0].keys()
    writer.writerow(columns)
    for line in data:
        row = []
        for column in columns:
            row += [line[column]]
        writer.writerow(row)

if os.path.exists(size_file):
    os.remove(size_file)

shutil.copy(size_file_wth_date, size_file)

if os.path.exists(change_file):
    os.remove(change_file)

with open(change_file, 'w', encoding="UTF-16") as csvfile:  # UTF-16 because Excel is stupid
    writer = csv.writer(csvfile, delimiter=';', dialect='excel')
    data = change_data(tertial)
    columns = data[0].keys()
    writer.writerow(columns)
    for line in data:
        row = []
        for column in columns:
            row += [line[column]]
        writer.writerow(row)
