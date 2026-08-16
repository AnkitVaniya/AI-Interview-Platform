import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.code_executor import evaluate_submission

TEST_CASES = [
    {"input": "2 3", "expected_output": "5"},
    {"input": "10 20", "expected_output": "30"},
]


def test_correct_solution_is_accepted():
    code = "a, b = map(int, input().split())\nprint(a + b)"
    result = evaluate_submission(code, TEST_CASES)
    assert result["verdict"] == "Accepted"
    assert result["passed_cases"] == 2


def test_wrong_solution_is_rejected():
    code = "a, b = map(int, input().split())\nprint(a - b)"
    result = evaluate_submission(code, TEST_CASES)
    assert result["verdict"] == "Wrong Answer"
    assert result["passed_cases"] == 0


def test_crashing_code_reports_error():
    code = "raise ValueError('boom')"
    result = evaluate_submission(code, TEST_CASES)
    assert result["verdict"] == "Error"


def test_infinite_loop_times_out():
    code = "while True: pass"
    result = evaluate_submission(code, TEST_CASES)
    assert result["verdict"] == "Timeout"
