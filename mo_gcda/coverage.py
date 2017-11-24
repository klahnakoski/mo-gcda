# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)

from __future__ import division
from __future__ import unicode_literals

from zipfile import ZipFile

from mo_dots import Data, Null
from mo_files import File
from mo_logs import Log

from mo_gcda import gcno, gcda


def line_coverage(gcno_file, gcda_file):
    # map from id to blocks to lines covered
    # list coverable lines by file
    lookup = build_gcno_line_table(gcno_file)
    counts = accumulate_counts(gcda_file, lookup)
    for file_name, lines in counts.items():
        covered = [l for l, c in lines.items() if c > 0]
        uncovered = [l for l, c in lines.items() if c == 0]
        if lines:
            yield {
                "source": {
                    "file": {
                        "name": file_name
                    },
                    "covered": covered,
                    "uncovered": uncovered,
                    "total_covered": len(covered),
                    "total_uncovered": len(uncovered),
                    "percentage_covered": len(covered)/(len(covered) + len(uncovered))

                }
            }


def accumulate_counts(gcda_file, lookup):
    """
    :param gcda_file: zipfile of gcda directory
    :param lookup: gcno lookup file
    :return:  map from file to line to count
    """
    output = Data()
    with ZipFile(File(gcda_file).abspath) as zipped:
        for num, zip_file in enumerate(zipped.filelist):
            if zip_file.file_size == 0:
                continue
            if not zip_file.filename.endswith(".gcda"):
                continue
            Log.note("process gcda {{file}}", file=zip_file.filename)
            try:
                with zipped.open(zip_file.filename) as source:
                    for c in gcda.stream_counts(source):
                        uid, counters = c['uid'], c['counters']
                        blocks = lookup.get(uid, Null)
                        for b, c in zip(blocks, counters):
                            if c:
                                for l in b:
                                    output[l.file][l.line] += c
            except Exception as e:
                Log.warning("{{filename}} could not be processed", filename=zip_file.filename, cause=e)
    return output


def build_gcno_line_table(zipfile):
    """
    Firefox gcno are too big to fit in 32bit memory

    :param zipfile: zipped directory of gcno files
    :return: gcno lookup table: map from function to array of blocks containing lines
    """

    output={}
    with ZipFile(File(zipfile).abspath) as zipped:
        for num, zip_name in enumerate(zipped.namelist()):
            if num==0:
                continue
            Log.note("process gcno {{file}}", file=zip_name)
            notes = gcno.read(zipped.open(zip_name))
            for func in notes.functions:
                uid = (func.id, func.config_checksum, func.line_checksum)
                # if uid in output:
                #     Log.note("duplicate function {{ func}}", func=func)
                output[uid] = [b.lines for b in func.blocks]
    return output

