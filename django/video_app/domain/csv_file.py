# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv


class CsvFileManager(object):
    def __init__(self, csv_fullname, column_names, has_header=False):
        self.csv_fullname = csv_fullname
        self.column_names = column_names
        self.has_header = has_header

    def get_records(self, columns):
        records = {}
        with open(self.csv_fullname, mode=b'rU') as f:
            rows = csv.reader(f, delimiter=b',', quotechar=b'"')
            for counter, row in enumerate(rows):
                if counter == 0 and self.has_header:
                    continue
                try:
                    records[counter] = dict(
                        [(name, row[self.column_names[name]].strip().decode('ascii')) for name in columns])
                except UnicodeDecodeError:
                    records[counter] = {'error': "it was not a ascii-encoded unicode string"}
        return records
