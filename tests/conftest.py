"""
Test fixtures and configuration for pytest
"""
import asyncio

import pytest

from data_query_server.server import DataQueryServer, data_server


@pytest.fixture
async def data_server_instance():
    """Fixture that provides an initialized DataQueryServer instance"""
    server = DataQueryServer()
    await server.initialize()
    yield server
    server.cleanup()


@pytest.fixture
async def initialized_global_server():
    """Fixture that initializes the global data_server instance"""
    await data_server.initialize()
    yield data_server
    data_server.cleanup()


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
