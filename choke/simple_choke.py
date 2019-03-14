"""Implementation of simple choke based on dictionary of lists."""
import bisect
from collections import defaultdict
from time import time
from choke.choke_base import BaseChokeManager


class SimpleChokeManager(BaseChokeManager):
    """Simplest, non-thread safe choke utilizing dict mapping tags to lists of timestamps."""

    def get_records(self, tag):
        """Get records corresponding to given tag."""
        return tuple(self.records[tag])

    def __init__(self, time_source=time):
        super(SimpleChokeManager, self).__init__(time_source)
        self.records = defaultdict(list)

    def _register_timestamp(self, tag, timestamp):
        bisect.insort(self.records[tag], timestamp)

    def _ltrim_timestamps(self, tag, max_timestamp):
        index = bisect.bisect_right(self.records[tag], max_timestamp)
        self.records[tag] = self.records[tag][index:]

    def _count_timestamps_for_window(self, tag, timestamp, window_length):
        left = bisect.bisect_right(self.records[tag], timestamp - window_length)
        right = bisect.bisect_right(self.records[tag], timestamp)
        return right - left
