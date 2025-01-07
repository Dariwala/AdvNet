import os
import signal
import subprocess

def find_and_kill_process(process_name):
    try:
        # Find the PID of the process
        result = subprocess.run(['pgrep', '-f', process_name], stdout=subprocess.PIPE)
        pids = result.stdout.decode().strip().split('\n')

        # Kill the process
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGTERM)
                # print(f"Process {pid} has been killed.")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    process_name = 'toy'
    find_and_kill_process(process_name)