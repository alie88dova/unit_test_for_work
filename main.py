import aiohttp
import pytest


async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)


class MockClientSession:
    def __init__(self, connector=None):
        self.connector = connector


    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def get(self, url):
        return MockClientResponse()


class TestContent:
    content = ['line 1', 'line 2', 'line 3']

    async def __aiter__(self):
        for item in self.content:
            yield item


class MockClientResponse:
    content = TestContent()

    def __init__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_logs(monkeypatch, capsys):

    monkeypatch.setattr(aiohttp, 'ClientSession', MockClientSession)

    cont = 'my_container'
    name = 'Test'
    await logs(cont, name)
    captured = capsys.readouterr()
    assert 'Test line 1' in captured.out
    assert 'Test line 2' in captured.out
    assert 'Test line 3' in captured.out

    # Дополнительные проверки, что код logs работает как ожидается