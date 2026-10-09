"""Start the local Streamlit dashboard and print its verified URL."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / '.local' / 'ed-discussion'
SERVER_FILE = DATA_DIR / 'server.json'
LOG_FILE = DATA_DIR / 'streamlit.log'
APP_FILE = PROJECT_ROOT / 'app.py'


def healthy(port):
    if not isinstance(port, int):
        return False
    try:
        with urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=1) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def available_port():
    for port in range(8501, 8600):
        with socket.socket() as listener:
            try:
                listener.bind(('127.0.0.1', port))
            except OSError:
                continue
            return port
    raise RuntimeError('No available local port between 8501 and 8599.')


def python_with_streamlit():
    candidate = (PROJECT_ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt'
                                            else 'bin/python'))
    for executable in (candidate, Path(sys.executable)):
        if not executable.is_file():
            continue
        check = subprocess.run([str(executable), '-c', 'import streamlit'],
                               capture_output=True, text=True, timeout=15)
        if check.returncode == 0:
            return executable
    raise RuntimeError('Streamlit is not installed. Install requirements.txt locally first.')


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        record = json.loads(SERVER_FILE.read_text(encoding='utf-8'))
        if record.get('app') == str(APP_FILE) and healthy(record.get('port')):
            print(f"http://localhost:{record['port']}")
            return
    except (FileNotFoundError, ValueError, TypeError):
        pass

    port = available_port()
    executable = python_with_streamlit()
    command = [str(executable), '-m', 'streamlit', 'run', str(APP_FILE),
               '--server.address=127.0.0.1', f'--server.port={port}',
               '--server.headless=true', '--browser.gatherUsageStats=false']
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             if os.name == 'nt' else 0)
    with LOG_FILE.open('a', encoding='utf-8') as log:
        process = subprocess.Popen(command, cwd=PROJECT_ROOT, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=flags, close_fds=True,
                                   start_new_session=(os.name != 'nt'))
    for _ in range(60):
        if healthy(port):
            SERVER_FILE.write_text(json.dumps({'app': str(APP_FILE), 'port': port,
                                               'pid': process.pid}), encoding='utf-8')
            print(f'http://localhost:{port}')
            return
        if process.poll() is not None:
            break
        time.sleep(0.5)
    if process.poll() is None:
        process.terminate()
    tail = LOG_FILE.read_text(encoding='utf-8', errors='replace')[-1500:]
    raise RuntimeError(f'Streamlit did not become ready. Recent log:\n{tail}')


if __name__ == '__main__':
    main()
