# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Tyler Blair (tblair@cs.dal.ca)

from __future__ import division
from __future__ import unicode_literals

from mo_dots import Data
from mo_logs import Log

from mo_gcda.gcno import read_i4, read_c, read_record_header, read_i8, read_u4



def stream_counts(source):
    """
    :param source: byte stream of gcda file
    :return: generator that yields just the counter records
    """

    data_record = read_record_header(source)
    while True:
        try:
            read_program_summary(source, data_record)
            function_record = read_record_header(source)
            while True:
                read_function_tags(source, function_record)
                while True:
                    counter_record = read_record_header(source)
                    if not counter_record._type:
                        return
                    if counter_record._type & 0x0FF00000 != FUNCTION_COUNTERS:
                        function_record = counter_record
                        break

                    read_function_counters(source, counter_record)
                    yield {
                        "uid": (function_record.id, function_record.config_checksum, function_record.line_checksum),
                        "counters": counter_record.counters
                    }
        except Exception as e:
            if "No more records" in e:
                return
            Log.error("Can not read record", cause=e)


def read(source):
    """
    :param source: byte stream of the gcda file
    :return: descriptive structure
    """
    output = Data(
        file_type=read_c(source, 1)[::-1],
        version=read_c(source, 1),
        stamp=read_i4(source)
    )

    records = output.records = []
    data_record = read_record_header(source)
    while True:
        try:
            read_program_summary(source, data_record)
            records.append(data_record)

            functions = data_record.functions = []
            function_record = read_record_header(source)
            while True:
                read_function_tags(source, function_record)
                functions.append(function_record)

                while True:
                    counter_record = read_record_header(source)
                    if not counter_record._type:
                        return output
                    if counter_record._type & 0x0FF00000 != FUNCTION_COUNTERS:
                        function_record = counter_record
                        break

                    read_function_counters(source, counter_record)
                    if not function_record.runs:
                        function_record.runs = []
                    if counter_record.run != len(function_record.runs):
                        Log.error("expecting function run information in order")
                    function_record.runs.append(counter_record)

        except Exception as e:
            if "No more records" in e:
                return output
            Log.error("Can not read record", cause=e)


def read_program_summary(source, record):
    if record._type != PROGRAM_SUMMARY:
        Log.error("Expecting program summary record got {{type|hex}}", type=record._type)
    record.checksum = read_i4(source)
    record.num_counters = read_i4(source)

    record.summary.checksum = read_u4(source)
    record.summary.num = read_u4(source)
    record.summary.runs = read_u4(source)
    record.summary.sum = read_i8(source)
    record.summary.run_max = read_i8(source)
    record.summary.sum_max = read_i8(source)
    record.summary.histogram = read_histogram_buckets(source, record)


def read_histogram_buckets(source, record):
    num, remainder = divmod(record._length - 11, 5)

    output = []
    for i in range(num):
        output.append(Data(
            num=read_i4(source),
            min_value=read_i8(source),
            cum_value=read_i8(source)
        ))

    junk = read_u4(source, remainder)
    return output


def read_function_tags(source, record):
    if record._type != FUNCTION_TAG:
        Log.error("Expecting function tags record got {{type|hex}}", type=record._type)
    if record._length != 3:
        return
    record.id = read_i4(source)
    record.line_checksum = read_u4(source)
    record.config_checksum = read_u4(source)


def read_function_counters(source, record):
    if record._type & 0x0FF00000 != FUNCTION_COUNTERS:
        Log.error("Expecting function counters record got {{type|hex}}", type=record._type)
    if record._length % 2:
        Log.error("expecting an even number")
    record.run, _ = divmod((record._type & 0x000FFFFF) - 0x10000, 0x20000)
    record.counters = read_i8(source, int(record._length / 2))


def do_not_know_how_to_handle_multiple_runs(source, record):
    Log.error("not implemented yet")


PROGRAM_SUMMARY = int(0xa3000000)
FUNCTION_TAG = 0x01000000
FUNCTION_COUNTERS = 0x01a00000

