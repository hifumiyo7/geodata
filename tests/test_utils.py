import pytest
import redis.exceptions
from utils.ip_utils import isIP
from utils.redis_utils import raise_function, redis_wrapping_function


@pytest.mark.parametrize(
    "ip, expected",
    [
        ("1.1.1.1", True),
        ("1.2.46.76", True),
        ("1.1.1", False),
        ("1.1.1.256", False),
        ("1.1.1.-1", False),
        ("1.b.c.d", False),
        ("", False),
        ("aa", False),
    ],
)
class TestIsIP:
    def test_isIP(self, ip, expected):
        assert isIP(ip) == expected


class TestRaiseFunction:
    def test_positive_path(self):
        def func():
            return "success"

        wrapped_func = raise_function(func)
        assert wrapped_func() == "success"

    def test_negative_path(self):
        def func():
            raise Exception("error")

        wrapped_func = raise_function(func)
        assert wrapped_func() == ('{"error": "error"}', 500)

    def test_negative_path_redis(self):
        def func():
            raise redis.exceptions.ConnectionError("error")

        wrapped_func = raise_function(func)
        assert wrapped_func() == ('{"error": "Redis connection error"}', 500)


class TestRedisWrappingFunction:
    def test_positive_path(self):
        def func():
            return "success"

        wrapped_func = redis_wrapping_function(func)
        assert wrapped_func() == "success"

    def test_negative_path_redis(self):
        def func():
            raise redis.exceptions.ConnectionError("error")

        wrapped_func = redis_wrapping_function(func)
        with pytest.raises(redis.exceptions.ConnectionError) as exc:
            wrapped_func()
        assert str(exc.value) == "error"
