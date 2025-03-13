import os

from slowapi import Limiter
from slowapi.util import get_remote_address

if os.getenv("TESTING") != "true":
    limiter = Limiter(key_func=get_remote_address)
else:

    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    limiter = DummyLimiter()
