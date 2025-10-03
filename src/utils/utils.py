import signal
import subprocess

def timeout_handler(signum, frame):
    raise TimeoutError("Function execution timed out")

def run_with_timeout(func, args=(), kwargs={}, timeout=5):
    signal.signal(signal.SIGALRM, timeout_handler)
    if timeout >= 0:
        signal.alarm(timeout)

    result = func(*args, **kwargs)
    signal.alarm(0)
    return result

def run_command(command: list[str]):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout, stderr
