# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Tyler Blair (tblair@cs.dal.ca)

from __future__ import division
from __future__ import unicode_literals

from mo_files import File
from mo_logs import Log
from mo_testing.fuzzytestcase import FuzzyTestCase
from mo_times import Timer

from mo_gcda import gcno, gcda, coverage


class Test(FuzzyTestCase):
    def test_gcno_file_1(self):
        # TEST NO PARSE ERRORS
        with open_binary_stream(File("tests/resources/nsWindowDataSource.gcno")) as source:
            result = gcno.read(source)
        Log.note("gcno file: {{result|json}}", result=result)

    def test_gcno_file_big(self):
        with Timer("time to read big file"):
            with open_binary_stream(File("tests/resources/TestJSImplGenBinding.gcno")) as source:
                result = gcno.read(source)
        Log.note("number of functions: {{num}}", num=len(result.functions))

    def test_gcda_file_1(self):
        # TEST NO PARSE ERRORS
        with open_binary_stream(File("tests/resources/gfxPrefs.gcda")) as source:
            result = gcda.read(source)
        Log.note("gcda file: {{result|json}}", result=result)

    def test_platform(self):
        with open_binary_stream(File("tests/resources/Platform.gcno")) as source:
            result = gcno.read(source)
        Log.note("gcno: {{result|json}}", result=result)

        with open_binary_stream(File("tests/resources/Platform.gcda")) as source:
            result = gcda.read(source)
        Log.note("gcda: {{result|json}}", result=result)


    def test_zipped(self):
        result = coverage.line_coverage("tests/resources/gcno.zip", "tests/resources/gcda.zip")
        for r in result:
            Log.note("coverage {{cov}}", cov=r)


def open_binary_stream(file):
    return open(file.abspath, "rb")
