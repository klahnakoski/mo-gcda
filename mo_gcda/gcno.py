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

FUNCTION_RECORD = 0x01000000
BLOCKS_RECORD = 0x01410000
ARCS_RECORD = 0x01430000
LINES_RECORD = 0x01450000


def read(source):
    # https://github.com/mitchhentges/lcov-rs/wiki/File-format
    # https://github.com/gcc-mirror/gcc/blob/master/gcc/gcov-io.h

    output = Data(
        file_type=read_c(source, 1),
        version=read_c(source, 1),
        stamp=read_i4(source)
    )

    records = output.records = []
    function_record = read_record_header(source)
    while True:
        try:
            # FUNCTION
            read_function(source, function_record)
            records.append(function_record)

            # BLOCKS
            blocks = read_record_header(source)
            read_blocks(source, blocks)
            function_record.blocks = [Data(id=i, flags=flag) for i, flag in enumerate(blocks.block_flags)]

            while True:
                # ARCS
                arcs_record = read_record_header(source)
                if arcs_record._type != ARCS_RECORD:
                    lines_record = arcs_record
                    break
                read_arcs(source, arcs_record)
                function_record.blocks[arcs_record.source_block].arcs = arcs_record.arcs

            # LINES
            while True:
                read_lines(source, lines_record)
                function_record.blocks[lines_record.block_number].lines=lines_record.lines
                lines_record = read_record_header(source)
                if lines_record._type != LINES_RECORD:
                    function_record = lines_record
                    break

        except Exception as e:
            if "No more records" in e:
                return output
            Log.error("Can not read record", cause=e)


def read_record_header(source):
    try:
        _type = read_u4(source)
    except Exception as e:
        raise Log.error("No more records", cause=e)

    return Data(
        _type=_type,
        _length=read_u4(source)
    )


def read_function(source, record):
    if record._type != FUNCTION_RECORD:
        Log.error("Expecting function record got {{type|hex}}", type=record._type)
    record.id = read_i4(source)
    record.line_checksum = read_u4(source)
    record.config_checksum = read_u4(source)
    record.function_name = read_string(source)
    record.source_path = read_string(source)
    record.line_number = read_i4(source)


def read_lines(source, record):
    if record._type != LINES_RECORD:
        Log.error("Expecting lines record got {{type|hex}}", type=record._type)
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
    if record._type != BLOCKS_RECORD:
        Log.error("Expecting blocks record got {{type|hex}}", type=record._type)
    record.block_flags = read_u4(source, record._length)


def read_arcs(source, record):
    if record._type != ARCS_RECORD:
        Log.error("Expecting arcs record got {{type|hex}}", type=record._type)

    record.source_block = read_i4(source)
    arcs = record.arcs = []
    num, _ = divmod(record._length-1, 2)
    for _ in range(num):
        arcs.append({
            "destination_block": read_i4(source),
            "flags": read_u4(source)
        })


def read_i4(source):
    return struct.unpack("i", source.read(4))[0]


def read_i8(source, length=1):
    if length == 1:
        return struct.unpack("q", source.read(8))[0]
    else:
        return struct.unpack(text_type(length) + "q", source.read(length*8))


def read_u4(source, length=1):
    if length == 1:
        return struct.unpack("I", source.read(4))[0]
    else:
        return struct.unpack(text_type(length) + "I", source.read(length*4))


def read_c(source, length):
    return struct.unpack(text_type(4*length) + "s", source.read(4*length))[0]


def read_string(source):
    return read_c(source, read_i4(source)).decode("latin1").rstrip("\u0000")
