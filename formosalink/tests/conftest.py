import pytest


@pytest.fixture
def anyio_backend():
  # The relay uses asyncio queues and native asyncio WebSocket clients.
  return "asyncio"
