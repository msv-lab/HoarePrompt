import subprocess
import sys
import os


def run_pytest(pythonpath, pytest_script):
    env = os.environ.copy()
    env["PYTHONPATH"] = pythonpath
    command = [sys.executable, "-m", "pytest", pytest_script]
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)
    pythonpath = sys.argv[1]
    pytest_script = sys.argv[2]
    exit_code = run_pytest(pythonpath, pytest_script)
    sys.exit(exit_code)
