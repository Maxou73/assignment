from fastapi import FastAPI, HTTPException
import requests
import time
import threading

app = FastAPI()

# Global variables to control the game
# pong_time_ms = 1000
# game_running = False
# target_instance_url = None  # URL of the other server


@app.get("/ping")
def ping():
    """
    Endpoint to handle incoming ping requests.
    """
    return {"message": "pong"}


def send_ping():
    """
    Function to send a ping request to the other server.
    """
    global game_running, pong_time_ms, target_instance_url
    while game_running:
        try:
            response = requests.get(f"{target_instance_url}/ping")
            if response.status_code == 200:
                print(f"Received: {response.json()}")
        except Exception as e:
            print(f"Failed to send ping: {e}")
        time.sleep(pong_time_ms / 1000)


@app.post("/start")
def start_game(pong_interval: int, target_url: str):
    """
    Starts the ping-pong game with the given interval and target instance.
    """
    global pong_time_ms, game_running, target_instance_url
    pong_time_ms = pong_interval
    target_instance_url = target_url
    game_running = True
    threading.Thread(target=send_ping, daemon=True).start()
    return {"status": "Game started", "pong_time_ms": pong_time_ms}


@app.post("/pause")
def pause_game():
    """
    Pauses the game.
    """
    global game_running
    game_running = False
    return {"status": "Game paused"}


@app.post("/resume")
def resume_game():
    """
    Resumes the game with the previous interval.
    """
    global game_running
    if not target_instance_url:
        raise HTTPException(status_code=400, detail="Game not started yet")
    game_running = True
    threading.Thread(target=send_ping, daemon=True).start()
    return {"status": "Game resumed"}


@app.post("/stop")
def stop_game():
    """
    Stops the game.
    """
    global game_running
    game_running = False
    return {"status": "Game stopped"}
