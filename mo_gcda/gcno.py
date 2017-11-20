# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Tyler Blair (tblair@cs.dal.ca)

from __future__ import division
from __future__ import unicode_literals

import struct

from future.utils import text_type
from mo_dots import Data
from mo_logs import Log


# https://github.com/mitchhentges/lcov-rs/wiki/File-format
# https://github.com/gcc-mirror/gcc/blob/master/gcc/gcov-io.h


def read(source):
    output = Data(
        file_type=read_c(source, 1),
        version=read_c(source, 1),
        stamp=read_i4(source)
    )

    records = output.records = []
    while True:
        try:
            record = read_record_header(source)
            if not record.record_type:
                return output
            reader = TYPES.get(record.record_type, read_unknown)
            reader(source, record)
            if reader is not read_ignored:
                records.append(record)

        except Exception as e:
            if "No more records" in e:
                return output
            Log.error("Can not read record", cause=e)


def read_record_header(source):
    try:
        record_type = read_i4(source)
    except Exception as e:
        Log.error("No more records", cause=e)

    return Data(
        record_type=record_type,
        record_length=read_u4(source)
    )


def read_function_record(source, record):
    record.id = read_i4(source)
    record.line_checksum = read_u4(source)
    record.config_checksum = read_u4(source)
    record.function_name = read_string(source)
    record.source_path = read_string(source)
    record.line_number = read_i4(source)


def read_lines_record(source, record):
    block_number = read_i4(source)
    lines = []
    filename = None
    while True:
        line = read_i4(source)
        if not line:
            filename = read_string(source)
            if not filename:
                break
        else:
            lines.append((filename, line))
    record.block_number = block_number
    record.lines = lines


def read_blocks(source, record):
    record.block_flags = read_u4(source, record.record_length)


def read_unknown(source, record):
    Log.note("Not known record_type {{record_type|hex}}", record_type=record.record_type)
    read_c(source, record.record_length)


def read_ignored(source, record):
    read_c(source, record.record_length)


TYPES = {
    0x01000000: read_function_record,
    0x01410000: read_blocks,
    0x01430000: read_ignored,  # ARCS
    0x01450000: read_lines_record
}


def read_i4(source):
    return struct.unpack("i", source.read(4))[0]


def read_u4(source, length=1):
    if length == 1:
        return struct.unpack("I", source.read(4))[0]
    else:
        return struct.unpack(text_type(length) + "I", source.read(length*4))


def read_c(source, length):
    return struct.unpack(text_type(4*length) + "s", source.read(4*length))[0]


def read_string(source):
    return read_c(source, read_i4(source)).decode("latin1").rstrip("\u0000")
