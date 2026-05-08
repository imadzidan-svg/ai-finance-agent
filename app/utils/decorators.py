import time
from functools import wraps

from app.utils.logger import logger


def execution_time(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()

        logger.info(
            f"{func.__name__} executed in {end - start:.4f} seconds"
        )

        return result

    return wrapper

def simple_cache(func):

    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):

        key = str(args) + str(kwargs)

        if key in cache:

            logger.info(f"Cache hit for {func.__name__}")

            return cache[key]

        result = func(*args, **kwargs)

        cache[key] = result

        logger.info(f"Cache stored for {func.__name__}")

        return result

    return wrapper

def retry(max_attempts=3):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(max_attempts):

                try:

                    return func(*args, **kwargs)

                except Exception as e:

                    logger.error(
                        f"{func.__name__} failed on attempt "
                        f"{attempt + 1}: {str(e)}"
                    )

            raise Exception(
                f"{func.__name__} failed after {max_attempts} attempts"
            )

        return wrapper

    return decorator