import sys
import requests
import subprocess
import os
import time
import platform

# Base URLs for the instances
INSTANCE_1_URL = "http://localhost:8000"
INSTANCE_2_URL = "http://localhost:8001"
# Paths to the server files (update these paths as per your setup)
SERVER_SCRIPT = "server.py"  # The FastAPI server script file


def start_servers():
    """
    Start both FastAPI servers as background processes.
    """
    try:


        os_name = platform.system()
        current_dir = os.getcwd()
        if os_name == "Windows":

            # Start server 1 on port 8000
            subprocess.Popen(["start", "cmd", "/k","uvicorn server:app --host 0.0.0.0 --port 8000"], shell=True)

            # Start server 2 on port 8001
            subprocess.Popen(["start", "cmd", "/k","uvicorn server:app --host 0.0.0.0 --port 8001"], shell=True)

        elif os_name == "Darwin":  # macOS
            # Start server 1 on port 8000
            apple_script = f'''
            tell application "Terminal"
                do script "cd '{current_dir}' && uvicorn server:app --host 0.0.0.0 --port 8000"
            end tell
            '''
            subprocess.run(["osascript", "-e", apple_script])
            # Start server 2 on port 8001

            apple_script = f'''
            tell application "Terminal"

                do script "cd '{current_dir}' && uvicorn server:app --host 0.0.0.0 --port 8001"
            end tell
            '''
            subprocess.run(["osascript", "-e", apple_script])
        # Allow some time for the servers to start
        time.sleep(2)
        print("Servers started successfully.")
    except Exception as e:
        print(f"Failed to start servers: {e}")
def start(pong_time_ms):
    """
    Start the game with the given pong interval.
    """
    start_servers()  # Ensure servers are running
    try:
        requests.post(f"{INSTANCE_1_URL}/start", params={"pong_interval": pong_time_ms, "target_url": INSTANCE_2_URL})
        requests.post(f"{INSTANCE_2_URL}/start", params={"pong_interval": pong_time_ms, "target_url": INSTANCE_1_URL})
        print(f"Game started with interval: {pong_time_ms} ms")
    except Exception as e:
        print(f"Error starting the game: {e}")


def pause():
    try:
        requests.post(f"{INSTANCE_1_URL}/pause")
        requests.post(f"{INSTANCE_2_URL}/pause")
        print("Game paused.")
    except Exception as e:
        print(f"Error pausing the game: {e}")


def resume():
    try:
        requests.post(f"{INSTANCE_1_URL}/resume")
        requests.post(f"{INSTANCE_2_URL}/resume")
        print("Game resumed.")
    except Exception as e:
        print(f"Error resuming the game: {e}")


def stop():
    try:
        requests.post(f"{INSTANCE_1_URL}/stop")
        requests.post(f"{INSTANCE_2_URL}/stop")
        print("Game stopped.")
    except Exception as e:
        print(f"Error stopping the game: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pong-cli.py <command> <param>")
        sys.exit(1)

    command = sys.argv[1]
    if command == "start":
        if len(sys.argv) != 3:
            print("Usage: python pong-cli.py start <pong_time_ms>")
            sys.exit(1)
        pong_time_ms = int(sys.argv[2])
        start(pong_time_ms)
    elif command == "pause":
        pause()
    elif command == "resume":
        resume()
    elif command == "stop":
        stop()
    else:
        print(f"Unknown command: {command}")
