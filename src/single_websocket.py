import websocket
import json
import threading

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None

    def on_message(self, ws, message):
        print(f"Received message: {message}")

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### Connection Closed ###")

    def on_open(self, ws):
        print("Connection Opened")
        # You can send a message or multiple messages here
        # Or you can move the message sending logic to a different method

    def send_message(self, message):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            try:
                self.ws.send(json.dumps(message))
            except websocket.WebSocketConnectionClosedException as e:
                print("WebSocket connection closed:", e)
                # Optionally, attempt to reconnect here
        else:
            print("WebSocket is not connected.")

    def run_forever(self):
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        websocket.enableTrace(True)
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def close(self):
        if self.ws:
            self.ws.close()

# Usage
if __name__ == "__main__":
    ws_client = WebSocketClient("ws://192.168.1.59:7125/klippysocket")
    ws_client.run_forever()

    # Example of sending a message
    message = {"id": 123, "method": "motion_report/dump_stepper", "params": {"name": "stepper_x"}}
    ws_client.send_message(message)

    # Keep the main thread running, or the script will exit
    try:
        while True:
            pass
    except KeyboardInterrupt:
        ws_client.close()

