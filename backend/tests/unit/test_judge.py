"""No database needed. Make judge.py pass these.

The last two are the ones that matter. If a submission can hang the server
or read the environment, the judge isn't done.
"""

import judge
from models import TestCase

ADD = "def add(a, b):\n    return a + b\n"


def test_correct_code_passes():
    tests = [TestCase(input=[1, 2], expected=3)]
    results = judge.run_submission(ADD, "add", tests)
    assert len(results) == 1
    assert results[0].passed is True
    assert results[0].got == 3


def test_wrong_answer_fails():
    wrong = "def add(a, b):\n    return a - b\n"
    results = judge.run_submission(wrong, "add", [TestCase(input=[5, 3], expected=8)])
    assert results[0].passed is False
    assert results[0].got == 2


def test_runs_every_test_not_just_the_first():
    tests = [
        TestCase(input=[1, 1], expected=99),
        TestCase(input=[2, 2], expected=4),
        TestCase(input=[3, 3], expected=6),
    ]
    results = judge.run_submission(ADD, "add", tests)
    assert [r.passed for r in results] == [False, True, True]


def test_lists_compare_properly():
    code = "def first_two(nums):\n    return nums[:2]\n"
    results = judge.run_submission(
        code, "first_two", [TestCase(input=[[9, 8, 7]], expected=[9, 8])]
    )
    assert results[0].passed is True


def test_syntax_error_is_a_fail_not_a_crash():
    results = judge.run_submission("def add(a, b)\n  return", "add",
                                   [TestCase(input=[1, 2], expected=3)])
    assert results[0].passed is False
    assert results[0].error


def test_missing_function_is_a_fail_not_a_crash():
    results = judge.run_submission(
        "x = 1", "add", [TestCase(input=[1, 2], expected=3)]
    )
    assert results[0].passed is False
    assert results[0].error


def test_crashing_code_is_a_fail_not_a_crash():
    code = "def add(a, b):\n    raise ValueError('nope')\n"
    results = judge.run_submission(code, "add", [TestCase(input=[1, 2], expected=3)])
    assert results[0].passed is False
    assert results[0].error


def test_printing_does_not_break_the_result():
    code = "def add(a, b):\n    print('debugging')\n    return a + b\n"
    results = judge.run_submission(code, "add", [TestCase(input=[1, 2], expected=3)])
    assert results[0].passed is True


def test_infinite_loop_times_out():
    # if this test hangs forever instead of failing, you have no timeout
    code = "def add(a, b):\n    while True:\n        pass\n"
    results = judge.run_submission(code, "add", [TestCase(input=[1, 2], expected=3)])
    assert results[0].passed is False
    assert results[0].error


def test_submission_cannot_read_the_environment():
    # a submission must not be able to see DATABASE_URL. if this fails you're
    # running the code in this process instead of a locked down subprocess
    code = (
        "import os\n"
        "def add(a, b):\n"
        "    return os.environ.get('DATABASE_URL', 'hidden')\n"
    )
    results = judge.run_submission(code, "add", [TestCase(input=[1, 2], expected=3)])
    assert results[0].got in (None, "hidden") or results[0].error
