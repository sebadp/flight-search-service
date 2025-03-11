import pytest
import pytest_asyncio
import json
from cache import get_cached_response, set_cache_response


class FakeRedis:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def setex(self, key, ttl, value):
        self.store[key] = value

    async def flushdb(self):
        self.store = {}

    async def close(self):
        pass


@pytest_asyncio.fixture
async def fake_redis():
    redis = FakeRedis()
    await redis.flushdb()
    yield redis
    await redis.close()


@pytest.mark.asyncio
async def test_get_cached_response_no_value(fake_redis):
    """
    Test that get_cached_response returns None when the key is not found.
    """
    result = await get_cached_response(fake_redis, "nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_get_cached_response_empty_list(fake_redis):
    """
    Test that get_cached_response returns an empty list when the key is found but the value is an empty list.
    """
    key = "empty_list"
    fake_redis.store[key] = json.dumps([])
    result = await get_cached_response(fake_redis, key)
    assert result == []


@pytest.mark.asyncio
async def test_get_cached_response_non_empty(fake_redis):
    """
    Test that get_cached_response returns the correct value when the key is found and the value is not empty.
    """
    key = "non_empty"
    data = {"foo": "bar"}
    fake_redis.store[key] = json.dumps(data)
    result = await get_cached_response(fake_redis, key)
    assert result == data


@pytest.mark.asyncio
async def test_set_cache_response(fake_redis):
    """
    Test that set_cache_response stores the correct value in the cache.
    """
    key = "test_key"
    data = {"data": [1, 2, 3]}
    await set_cache_response(fake_redis, key, data)
    cached = fake_redis.store.get(key)
    assert cached is not None
    assert json.loads(cached) == data


@pytest.mark.asyncio
async def test_set_and_get_integration(fake_redis):
    """
    Test that set_cache_response and get_cached_response work together as expected
    """
    key = "integration_test"
    data = {"a": 1, "b": [2, 3]}
    await set_cache_response(fake_redis, key, data)
    result = await get_cached_response(fake_redis, key)
    assert result == data
