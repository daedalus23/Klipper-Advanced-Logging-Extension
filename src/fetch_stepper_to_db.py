import asyncio
import websockets
import json

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Float


# Define the database model
Base = declarative_base()

class StepperData(Base):
    __tablename__ = 'stepper_data'
    id = Column(Integer, primary_key=True)
    interval = Column(Integer)
    count = Column(Integer)
    add_value = Column(Integer)
    start_position = Column(Float)
    start_mcu_position = Column(Integer)
    step_distance = Column(Float)
    first_clock = Column(Integer)
    first_step_time = Column(Float)
    last_clock = Column(Integer)
    last_step_time = Column(Float)

class StepperLogger:
    def __init__(self, base_url, stepper_names):
        self.base_url = base_url
        self.stepper_names = stepper_names
        self.data_queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()

    async def manage_stepper_connection(self, name):
        async with websockets.connect(self.base_url) as websocket:
            request = {"id": 123, "method": "motion_report/dump_stepper", "params": {"name": name}}
            await websocket.send(json.dumps(request))
            async for message in websocket:
                await self.data_queue.put((name, message))
                if self.shutdown_event.is_set():
                    break

    async def save_stepper_data(self, name):
        # Create async engine
        engine = create_async_engine(f"sqlite+aiosqlite:///{name}.db", echo=True)

        # Create tables (if not exist)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create async sessionmaker
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        while not self.shutdown_event.is_set() or not self.data_queue.empty():
            stepper_name, message = await self.data_queue.get()
            if stepper_name == name:
                try:
                    data = json.loads(message)
                    if 'params' in data:
                        async with async_session() as session:
                            for entry in data['params']['data']:
                                row_data = entry + [
                                    data['params']['start_position'],
                                    data['params']['start_mcu_position'],
                                    data['params']['step_distance'],
                                    data['params']['first_clock'],
                                    data['params']['first_step_time'],
                                    data['params']['last_clock'],
                                    data['params']['last_step_time']
                                ]
                                new_entry = StepperData(row_data)
                                session.add(new_entry)
                            await session.commit()
                            await asyncio.sleep(0)  # Yield to the event loop
                except json.JSONDecodeError:
                    print("Error parsing JSON message:", message)

    async def run(self):
        stepper_tasks = [self.manage_stepper_connection(name) for name in self.stepper_names]
        save_tasks = [self.save_stepper_data(name) for name in self.stepper_names]
        await asyncio.gather(*(stepper_tasks + save_tasks))

    async def start(self):
        await self.run()

    def stop(self):
        self.shutdown_event.set()

async def main():
    stepper_names = ["stepper_x", "stepper_y", "stepper_z"]
    logger = StepperLogger("ws://192.168.1.59:7125/klippysocket", stepper_names)
    await logger.start()


if __name__ == "__main__":
    asyncio.run(main())
