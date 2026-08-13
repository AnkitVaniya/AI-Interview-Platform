"""
Code execution service.

IMPORTANT — read before deploying anywhere public:
This runs submitted Python code directly via subprocess on the host machine.
That is FINE for local development and demoing to yourself, but it is NOT a
security sandbox — submitted code has full access to whatever the API
container can access. Do not expose this to untrusted users on the internet.

For production, replace `run_python_code()` internals with a call to Judge0
(self-hosted or API) or run each submission inside a locked-down, network-
disabled, resource-limited Docker container. The function signature below is
deliberately kept the same so that swap is a one-file change.
"""
import subprocess
import tempfile
import time
import os

TIMEOUT_SECONDS = 5


def run_python_code(code: str, stdin_input: str) -> tuple[str, float, bool]:
    """
    Runs `code` in a fresh subprocess, feeding it `stdin_input` on stdin.
    Returns (stdout_output, runtime_ms, timed_out).
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        script_path = f.name

    start = time.perf_counter()
    timed_out = False
    output = ""
    try:
        result = subprocess.run(
            ["python3", script_path],
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        output = result.stdout
        if result.returncode != 0 and not output:
            output = f"__ERROR__\n{result.stderr}"
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        os.unlink(script_path)

    runtime_ms = (time.perf_counter() - start) * 1000
    return output.strip(), runtime_ms, timed_out


def evaluate_submission(code: str, test_cases: list[dict]) -> dict:
    """
    Runs code against every test case and returns an overall verdict.
    test_cases: [{"input": "...", "expected_output": "..."}, ...]
    """
    passed = 0
    total_runtime = 0.0

    for case in test_cases:
        output, runtime_ms, timed_out = run_python_code(code, case["input"])
        total_runtime += runtime_ms

        if timed_out:
            return {
                "verdict": "Timeout",
                "runtime_ms": total_runtime,
                "passed_cases": passed,
                "total_cases": len(test_cases),
            }
        if output.startswith("__ERROR__"):
            return {
                "verdict": "Error",
                "runtime_ms": total_runtime,
                "passed_cases": passed,
                "total_cases": len(test_cases),
            }
        if output != case["expected_output"].strip():
            return {
                "verdict": "Wrong Answer",
                "runtime_ms": total_runtime,
                "passed_cases": passed,
                "total_cases": len(test_cases),
            }
        passed += 1

    return {
        "verdict": "Accepted",
        "runtime_ms": total_runtime,
        "passed_cases": passed,
        "total_cases": len(test_cases),
    }
