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

from mo_gcda import gcno


class TestGCNO(FuzzyTestCase):
    def test_file_1(self):
        with open_binary_stream(File("tests/resources/nsWindowDataSource.gcno")) as source:
            result = gcno.read(source)
        Log.note("result: {{result|json}}", result=result)


def open_binary_stream(file):
    return open(file.abspath, "rb")
