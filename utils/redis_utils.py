import json
import redis
import time


def redis_wrapping_function(func, retries=3):
    def wrapper(*args, **kwargs):
        retry_count = retries
        while True:
            try:
                return func(*args, **kwargs)
            except redis.exceptions.ConnectionError as exc:
                time.sleep(1)
                if retry_count <= 0:
                    raise exc
                retry_count -= 1

    return wrapper


def raise_function(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.exceptions.ConnectionError as exc:
            return json.dumps({"error": "Redis connection error"}), 500
        except Exception as exc:
            return json.dumps({"error": str(exc)}), 500

    return wrapper


@redis_wrapping_function
def set(r: redis.Redis, key: str, value: str, *args, **kwargs) -> bool:
    return r.set(key, value, *args, **kwargs)


@redis_wrapping_function
def exists(r: redis.Redis, key: str):
    return r.exists(key)


@redis_wrapping_function
def get(r: redis.Redis, key: str):
    return r.get(key)


@redis_wrapping_function
def delete(r: redis.Redis, key: str):
    return r.delete(key)


@redis_wrapping_function
def keys(r: redis.Redis):
    return r.keys()
