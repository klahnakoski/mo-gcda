# More GCDA - Read gcno/gcda with pure Python!

## Overview

This is a lightwight library that can read `*.gcno` and `*.gcda` files that come from gcc code coverage builds. This is useful on platforms and configurations that are missing lcov or gcc; like your production machines and Windows dev.



### Installing PyPy

You will require PyPy to process the larger gcno/gcda zipped directories.

    c:\pypy\pypy.exe -m ensurepip
    c:\pypy\bin\pip.exe install -r requirements.txt