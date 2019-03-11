"""Common functionallities used across choke package."""
import abc
import logging
import time


class BaseChokeManager(abc.ABC):
    """ABC for other choke managers."""

    logger_name = 'choke'

    def __init__(self, time_source=time):
        self.time_source = time_source

    def count_records(self, tag, window_length, prune=True):
        """Get count of records for given tag in given window, optionally pruning old records."""
        timestamp = self.time_source()
        logger = logging.getLogger(self.logger_name)

        if prune:
            self.prune(tag, window_length, timestamp)

        logger.debug('Checking cardinality of timestamps set for tag %s in recent window.', tag)
        count = self._count_timestamps_for_window(tag, timestamp, window_length)
        logger.debug('Number of records for tag %s in last window of length %s: %d',
                     tag, window_length, count)

        return count

    def prune(self, tag, window_length, ref_timestamp=None):
        """Prune timestamps for the given tag outside of given window."""
        logger = logging.getLogger('choke')
        ref_timestamp = ref_timestamp or self.time_source()
        max_timestamp = ref_timestamp - window_length

        logger.debug('Pruning timestamps below %s for tag %s.', max_timestamp, tag)
        self._ltrim_timestamps(tag, max_timestamp)

    def register_timestamp(self, tag):
        """Register new timestamp for given tag and window."""
        timestamp = self.time_source()
        logger = logging.getLogger('redis_choke')

        self._register_timestamp(tag, timestamp)
        logger.debug('New timestamp %s registered for tag %s.', timestamp, tag)

    @abc.abstractmethod
    def _count_timestamps_for_window(self, tag, timestamp, window_length):
        pass

    @abc.abstractmethod
    def _ltrim_timestamps(self, tag, max_timestamp):
        pass

    @abc.abstractmethod
    def _register_timestamp(self, tag, timestamp):
        pass
