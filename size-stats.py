#!/usr/bin/env python3

import os
import csv
import datetime
import shutil

from lib.size_data import size_data, change_data

today = datetime.datetime.today().strftime('%Y-%m-%d')
tertial = "2022T3"

size_file_wth_date = f"output/cloc-{today}.csv"
size_file = f"output/cloc.csv"
change_file = f"output/cloc-change-{tertial}.csv"

if os.path.exists(size_file_wth_date):
    os.remove(size_file_wth_date)

with open(size_file_wth_date, 'w', encoding="UTF-16") as csvfile:  # UTF-16 because Excel is stupid
    writer = csv.writer(csvfile, delimiter=';', dialect='excel')
    print(os.path.basename(os.getcwd()))
    data = size_data(os.getcwd() + "/..")
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
    data = change_data(os.getcwd() + '/..', tertial)
    columns = data[0].keys()
    writer.writerow(columns)
    for line in data:
        row = []
        for column in columns:
            row += [line[column]]
        writer.writerow(row)
