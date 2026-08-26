"""Runs a user's code against a question's test cases.

READ THIS BEFORE YOU START.

This runs code that a stranger typed into a text box. Do NOT use exec() or
eval() in this process. If you do, a submission can read DATABASE_URL, drop
every table, or read any file on the machine that runs the API. That is not
a hypothetical, it's about four lines of Python.

The approach that works:
  1. write the user's code + a small runner into a temp file
  2. run it with subprocess.run([sys.executable, path], ...)
  3. timeout=SECONDS_PER_TEST so infinite loops die
  4. capture_output=True, pass the test input in as stdin or argv
  5. parse the runner's json output back out

The runner is the bit you write that imports nothing, calls
function_name(*test.input), and prints json.dumps(result).

Things that will go wrong and need handling, not crashing:
  - the code doesn't define function_name at all
  - the code has a syntax error
  - the code loops forever  -> subprocess.TimeoutExpired
  - the code prints stuff    -> don't confuse it with the result
  - the code returns something json can't serialise
"""

import json  # noqa: F401
import subprocess  # noqa: F401
import sys  # noqa: F401

from models import TestCase, TestResult

SECONDS_PER_TEST = 5


def run_one_test(code: str, function_name: str, test: TestCase) -> TestResult:
    # run code in a subprocess, call function_name(*test.input), compare to
    # test.expected. a crash or timeout is a failed test, not an exception
    raise NotImplementedError


def run_submission(
    code: str, function_name: str, tests: list[TestCase]
) -> list[TestResult]:
    # run every test, return a result for each. don't stop at the first fail,
    # the user wants to see all of them
    raise NotImplementedError
