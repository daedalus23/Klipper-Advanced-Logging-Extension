import asyncio
import sys
import time

import websockets
import json
import threading

from datetime import datetime
from move_test import move_test


class StepperLogger:
    def __init__(self, base_url, module, stepper_name):
        self.consumer_task = None
        self.processor_task = None
        self.base_url = base_url
        self.module = module
        self.stepper_name = stepper_name
        self.shutdown_event = asyncio.Event()
        self.received_messages = asyncio.Queue()

    async def manage_stepper_connection(self):
        try:
            async with websockets.connect(self.base_url) as websocket:
                request = {"id": 123, "method": self.module, "params": {"name": self.stepper_name}}
                await websocket.send(json.dumps(request))
                async for message in websocket:
                    try:
                        await asyncio.wait_for(self.received_messages.put((self.stepper_name, message)), timeout=0.1)
                    except asyncio.TimeoutError:
                        continue
                    if self.shutdown_event.is_set():
                        break
        except asyncio.CancelledError:
            pass

    async def process_messages(self):
        while not self.shutdown_event.is_set():
            try:
                if not self.received_messages.empty():
                    try:
                        name, message = await asyncio.wait_for(self.received_messages.get(), timeout=0.1)
                    except asyncio.TimeoutError:
                        continue
                    # Process the message here
                    with open("data_stream.txt", "a") as file:
                        current_time = datetime.now()
                        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        file.write(f"{timestamp_str} - {name}: {message}\n")
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

    async def run(self):
        self.consumer_task = asyncio.create_task(self.manage_stepper_connection())
        self.processor_task = asyncio.create_task(self.process_messages())
        await asyncio.gather(self.consumer_task, self.processor_task)

    def start(self):
        self.thread = threading.Thread(target=self.thread_target)
        self.thread.start()

    def thread_target(self):
        asyncio.run(self.run())

    def stop(self):
        self.shutdown_event.set()
        self.consumer_task.cancel()
        self.processor_task.cancel()
        self.thread.join()

# Running multiple StepperLogger instances in separate threads
def main():
    loggers = [
        StepperLogger("ws://192.168.1.59:7125/klippysocket", "motion_report/dump_stepper", "stepper_x"),
        StepperLogger("ws://192.168.1.59:7125/klippysocket", "motion_report/dump_stepper", "stepper_y")
    ]

    # Start each logger in a separate thread
    for logger in loggers:
        logger.start()

    move_test(1000)
    time.sleep(5)   # Can't figure out how to properly stop the async loop so this halts it for until the data can be saved

    # Stop each logger
    for logger in loggers:
        logger.stop()

if __name__ == "__main__":
    main()
