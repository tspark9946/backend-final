import asyncio
from collections.abc import Callable
 
class EventExecutor:
    def __init__(self):
        self.events = []
 
    def add_event(self, event: Callable, *args, **kwargs):
        self.events.append((event, args, kwargs))
 
    async def run(self):
        for event, args, kwargs in self.events:
            if asyncio.iscoroutinefunction(event):
                await event(*args, **kwargs)
            else:
                event(*args, **kwargs)
 
class Lifespan:
    def __init__(self, timeout = None):
        self.startup_events = EventExecutor()
        self.shutdown_runner = EventExecutor()
        self.timeout = timeout
        self.__states = None
 
    def add_startup(self, event, *args, **kwargs):
        self.startup_events.add_event(event, *args, **kwargs)
 
    def add_shutdown(self, event, *args, **kwargs):
        self.shutdown_runner.add_event(event, *args, **kwargs)
 
    @property
    def states(self):
        if self.__states is not None and not isinstance(self.__states, dict):
            raise ValueError("States must be a dictionary or None")
        return self.__states
 
    @states.setter
    def states(self, value):
        if isinstance(value, Callable):
            self.__states = value()
        else:
            self.__states = value
 
    async def __aenter__(self):
        if self.timeout:
            async with asyncio.timeout(self.timeout):
                await self.startup_events.run()
        else:
            await self.startup_events.run()
        return self
 
    async def __aexit__(self, exc_type, exc, tb):
        if self.timeout:
            async with asyncio.timeout(self.timeout):
                await self.shutdown_runner.run()
        else:
            await self.shutdown_runner.run()
        return None
 
    async def lifespan(self, app):
        await self.__aenter__()
        try:
            yield self.states
        finally:
            await self.__aexit__(None, None, None)