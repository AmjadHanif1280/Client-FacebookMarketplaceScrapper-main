"""
This was a total failure ignore this file - Aidan (05/03/2023)
"""
import os
import signal
import subprocess
import sys

python_executable = sys.executable
scripts = [
    "Telegram-Bot.py",
    "MarketplaceBot.py",
    "cronjob_for_proxies.py",
    "MarketplaceAPI.py",
]

processes = []
for script in scripts:
    process = subprocess.Popen([python_executable, script], preexec_fn=os.setsid)
    processes.append(process)

# Wait for all the processes to finish
for process in processes:
    process.wait()

# Terminate all the processes
os.killpg(os.getpgid(0), signal.SIGTERM)
