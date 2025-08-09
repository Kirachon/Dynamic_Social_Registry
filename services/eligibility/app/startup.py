import asyncio
from fastapi import FastAPI
from .outbox_publisher import publish_loop
from .consumer import consume_registry

_tasks = []

def setup_background(app: FastAPI):
    @app.on_event("startup")
    async def _start():
        _tasks.append(asyncio.create_task(publish_loop()))
        _tasks.append(asyncio.create_task(consume_registry()))

    @app.on_event("shutdown")
    async def _stop():
        for t in _tasks:
            t.cancel()

