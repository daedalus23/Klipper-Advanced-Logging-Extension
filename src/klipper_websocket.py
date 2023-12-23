import asyncio
import time

import websockets
import json
import threading

from datetime import datetime


class StepperLogger:
    def __init__(self, base_url, module, stepper_name):
        self.base_url = base_url
        self.module = module
        self.stepper_name = stepper_name
        self.shutdown_event = asyncio.Event()
        self.received_messages = asyncio.Queue()

    async def manage_stepper_connection(self):
        async with websockets.connect(self.base_url) as websocket:
            request = {"id": 123, "method": self.module, "params": {"name": self.stepper_name}}
            await websocket.send(json.dumps(request))
            async for message in websocket:
                await self.received_messages.put((self.stepper_name, message))
                if self.shutdown_event.is_set():
                    break

    async def process_messages(self):
        while not self.shutdown_event.is_set():
            if not self.received_messages.empty():
                name, message = await self.received_messages.get()
                # Process the message here
                with open("data_stream.txt", "a") as file:
                    current_time = datetime.now()
                    timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    file.write(f"{timestamp_str} - {name}: {message}\n")
            await asyncio.sleep(0.1)

    async def run(self):
        consumer_task = asyncio.create_task(self.manage_stepper_connection())
        processor_task = asyncio.create_task(self.process_messages())
        await asyncio.gather(consumer_task, processor_task)

    def start(self):
        self.thread = threading.Thread(target=self.thread_target)
        self.thread.start()

    def thread_target(self):
        asyncio.run(self.run())

    def stop(self):
        self.shutdown_event.set()
        self.thread.join()

# Running multiple StepperLogger instances in separate threads
def main():
    loggers = [
        StepperLogger("ws://192.168.1.59:7125/klippysocket", "motion_report/dump_stepper", "stepper_x"),
        StepperLogger("ws://192.168.1.59:7125/klippysocket", "motion_report/dump_stepper", "stepper_y"),
        StepperLogger("ws://192.168.1.59:7125/klippysocket", "motion_report/dump_stepper", "stepper_z")
    ]

    # Start each logger in a separate thread
    for logger in loggers:
        logger.start()

    time.sleep(300)

    # Stop each logger
    for logger in loggers:
        logger.stop()

if __name__ == "__main__":
    main()
