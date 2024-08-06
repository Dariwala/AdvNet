import pexpect
import multiprocessing
import concurrent.futures
import time
import os
# from config import parent_folder
parent_folder = "/home/shehab/Desktop/"

def create_server(is_mp, stop_event):
    # Combine commands into a single command string
    if is_mp:
        commands = f"cd {parent_folder}picoquic && ./server_toy_mp"
    else:
        commands = f"cd {parent_folder}picoquic && ./server_toy"
    pem_passphrase = '1234'

    try:
        # Spawn a child process to run the commands
        child = pexpect.spawn("/bin/bash", timeout=6000)

        # Send the commands to the shell
        child.sendline(commands)

        # Wait for the prompt asking for the PEM passphrase
        child.expect('Enter PEM pass phrase:')

        # Send the PEM passphrase to the process
        child.sendline(pem_passphrase)
        # print("Server started")
        while not stop_event.is_set():
            # os.system("sleep 0.1")
            # Check if the child process has terminated
            if not child.isalive():
                break
            # time.sleep(0.1)  # Sleep for a while before checking again

        # If stop_event is set, terminate the child process
        if stop_event.is_set() and child.isalive():
            child.terminate()
            # print("Server ended")

    except pexpect.TIMEOUT:
        print("Timeout reached. Process took too long.")
    except pexpect.EOF:
        print("EOF reached. Process finished.")
    except pexpect.ExceptionPexpect as e:
        print(f"An error occurred: {e}")

def main():
    # Start the create_server function in a separate process
    server_process = multiprocessing.Process(target=create_server, args=(False,))
    server_process.start()

    # Continue executing other commands asynchronously
    for i in range(10):
        print(f"Main process is running: {i}")
        time.sleep(1)
    
    # Optionally, wait for the server process to complete
    server_process.join()
    print("Server creation process has completed.")

if __name__ == "__main__":
    main()
