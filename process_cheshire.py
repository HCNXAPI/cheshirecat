from flask import Flask, request, jsonify
import threading
import queue
import json
import time
import cheshire_cat_api as ccat

app = Flask(__name__)

config = ccat.Config(
    base_url="192.168.0.1",
    port=1865,
    user_id="user1",
    auth_key="",
    secure_connection=False
)

# Cambia da un semplice dizionario a una mappa di eventi per user_id
response_events = {}

def on_open():
    print("Connection opened!")

def on_message(message: str):
    data = json.loads(message)
    user_id = data.get('user_id')
    if data['type'] == 'chat':
        content = data['content']
    else:
        content = "Tipo non corrispondente a 'chat'"
    
    event, response_queue = response_events.get(user_id, (None, None))
    if event:
        response_queue.put(content)
        event.set()

def on_error(exception: Exception):
    print(str(exception))

def on_close(status_code: int, message: str):
    print(f"Connection closed with code {status_code}: {message}")

def send_via_websocket(user_id, message):
    event = threading.Event()
    response_queue = queue.Queue()
    response_events[user_id] = (event, response_queue)
    
    cat_client = ccat.CatClient(
        config=config,
        on_open=on_open,
        on_close=on_close,
        on_message=on_message,
        on_error=on_error
    )
    cat_client.connect_ws()
    while not cat_client.is_ws_connected:
        time.sleep(1)
    cat_client.send(message=json.dumps({"user_id": user_id, "message": message}))
    # Attendere l'evento invece di utilizzare sleep
    event.wait()
    response = response_queue.get()
    return response

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    user_id = data['user_id']
    message = data['message']
    
    response = send_via_websocket(user_id, message)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
