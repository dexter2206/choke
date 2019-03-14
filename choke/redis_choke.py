"""Redis-based implementation of throttling mechanism."""
from time import time
from choke.choke_base import BaseChokeManager


class RedisChokeManager(BaseChokeManager):
    """Basic class implementing low-level logic for choking resources."""

    def __init__(self, redis, time_source=time):
        super(RedisChokeManager, self).__init__(time_source)
        self.redis = redis

    def _register_timestamp(self, tag, timestamp):
        self.redis.zadd(tag, {timestamp: timestamp})

    def _ltrim_timestamps(self, tag, max_timestamp):
        self.redis.zremrangebyscore(tag, 0, max_timestamp)

    def _count_timestamps_for_window(self, tag, timestamp, window_length):
        return self.redis.zcount(tag, f'({timestamp - window_length}', timestamp)
