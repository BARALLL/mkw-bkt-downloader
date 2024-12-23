from collections.abc import Iterator
from threading import Lock
from time import time


# credits to that one guy on stackoverflow for the class
# https://stackoverflow.com/questions/20643184/using-python-threads-to-make-thousands-of-calls-to-a-slow-api-with-a-rate-limit/20644609#20644609
class RateLimiter(Iterator):
    """Iterator that yields a value at most once every 'interval' seconds."""

    def __init__(self, interval):
        self.lock = Lock()
        self.request_lock = Lock()
        self.interval = interval
        self.next_yield = 0

    def __next__(self):
        with self.lock:
            t = time.monotonic()
            if t < self.next_yield:
                time.sleep(self.next_yield - t)
                t = time.monotonic()
            self.next_yield = t + self.interval
