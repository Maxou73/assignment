import sys
import requests
import subprocess
import os
import time
import platform
import signal
import socket

# Base URLs for the instances

global INSTANCE_1_URL, INSTANCE_2_URL, PORT1, PORT2
# Paths to the server files (update these paths as per your setup)
SERVER_SCRIPT = "server.py"  # The FastAPI server script file

def is_port_occupied(port, host='0.0.0.0'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0




def start_servers():
    """
    Start both FastAPI servers as background processes.
    """
    try:
        PORT1 = 8000
        PORT2 = 8001
        os_name = platform.system()
        current_dir = os.getcwd()
        while is_port_occupied(PORT1):
            PORT1 += 2
            PORT2 += 2


        if os_name == "Windows":

            # Start server 1 on port 8000
            subprocess.Popen(["start", "cmd", "/k","uvicorn server:app --host 0.0.0.0 --port " + str(PORT1)], shell=True)

            # Start server 2 on port 8001
            subprocess.Popen(["start", "cmd", "/k","uvicorn server:app --host 0.0.0.0 --port " + str(PORT2)], shell=True)

        elif os_name == "Darwin":  # macOS
            # Start server 1 on port 8000
            apple_script = f'''
            tell application "Terminal"
                do script "cd '{current_dir}' && uvicorn server:app --host 0.0.0.0 --port {str(PORT1)}"
            end tell
            '''
            subprocess.run(["osascript", "-e", apple_script])
            # Start server 2 on port 8001

            apple_script = f'''
            tell application "Terminal"

                do script "cd '{current_dir}' && uvicorn server:app --host 0.0.0.0 --port {str(PORT2)}"
            end tell
            '''
            subprocess.run(["osascript", "-e", apple_script])
        # Allow some time for the servers to start
        time.sleep(2)
        print("Servers started successfully.")
    except Exception as e:
        print(f"Failed to start servers: {e}")
    return PORT1, PORT2


def stop_server(port):
    os_name = platform.system()
    try:
        if os_name in ["Darwin", "Linux"]:  # macOS/Linux
            result = os.popen(f"lsof -t -i:{port}").read().strip()  # Get PID
            if result:
                os.system(f"kill -9 {result}")  # Kill process
                print(f"Server on port {port} stopped.")
            else:
                print(f"No server found on port {port}.")
        elif os_name == "Windows":  # Windows
            result = os.popen(f"netstat -ano | findstr :{port}").read()
            lines = result.splitlines()
            for line in lines:
                parts = line.split()
                pid = parts[-1]  # PID is the last column
                os.system(f"taskkill /PID {pid} /F")  # Kill process
                print(f"Server on port {port} stopped.")
        else:
            print(f"Unsupported OS: {os_name}")
    except Exception as e:
        print(f"Error stopping server: {e}")


def stop_server_and_close_terminal(port):
    """
    Stop the server running on a given port and close its terminal, cross-platform.
    """
    os_name = platform.system()
    try:
        if os_name == "Windows":
            # Windows: Find the PID and terminate it
            result = os.popen(f"netstat -ano | findstr :{port}").read()
            lines = result.splitlines()
            if lines:
                pid = lines[0].split()[-1]  # Extract PID
                os.system(f"taskkill /PID {pid} /F")  # Kill the server process
                print(f"Server on port {port} stopped.")
                os.system("taskkill /F /IM cmd.exe")  # Close Command Prompt
            else:
                print(f"No server found on port {port}.")
        elif os_name == "Linux":
            # macOS/Linux: Find the PID and terminate it
            result = os.popen(f"lsof -t -i:{port}").read().strip()
            if result:
                pid = int(result)
                os.kill(pid, signal.SIGKILL)  # Kill the server process
                print(f"Server on port {port} stopped.")
                # Optionally, close the terminal window
                parent_pid = os.getppid()  # Get parent PID
                os.kill(parent_pid, signal.SIGTERM)  # Close the terminal window
            else:
                print(f"No server found on port {port}.")
        elif os_name == "Darwin":
                  # Find the PID of the process using the port
            result = os.popen(f"lsof -t -i:{port}").read().strip()
            if result:
                pid = int(result)
                os.kill(pid, signal.SIGKILL)  # Kill the server process
                print(f"Server on port {port} stopped.")

                # AppleScript to close the Terminal window
                apple_script = f'''
                tell application "Terminal"
                    close first window
                end tell
                '''
                subprocess.run(["osascript", "-e", apple_script])  # Execute AppleScript
            else:
                print(f"No server found on port {port}.")
        else:
            print(f"Unsupported OS: {os_name}")
    except Exception as e:
        print(f"Error stopping server: {e}")

def start(pong_time_ms):
    """
    Start the game with the given pong interval.
    """
    PORT1, PORT2 = start_servers()
     # Ensure servers are running

    INSTANCE_1_URL = "http://localhost:" + str(PORT1)
    INSTANCE_2_URL = "http://localhost:" + str(PORT2)
    try:
        requests.post(f"{INSTANCE_1_URL}/start", params={"pong_interval": pong_time_ms, "target_url": INSTANCE_2_URL, "throw_ball": True})
        requests.post(f"{INSTANCE_2_URL}/start", params={"pong_interval": pong_time_ms, "target_url": INSTANCE_1_URL, "throw_ball": False})
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
        stop_server(PORT1)
        stop_server(PORT2)
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
