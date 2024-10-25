import subprocess
import time

# List of scripts to run
scripts = ["telegram_bot/TelegramBot.py"]

# Function to run a script
def run_script(script):
    return subprocess.Popen(["python3", script])

# Dictionary to keep track of running processes
processes = {}

# Start all scripts
for script in scripts:
    processes[script] = run_script(script)

# Monitor the scripts and restart if any of them stop
try:
    while True:
        for script, process in processes.items():
            if process.poll() is not None:  # Process has terminated
                print(f"{script} has stopped. Restarting...")
                processes[script] = run_script(script)
        time.sleep(30)  # Check every 30 seconds
except KeyboardInterrupt:
    print("Stopping all scripts...")
    for process in processes.values():
        process.terminate()