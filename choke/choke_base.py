"""Common functionallities used across choke package."""
import abc
from functools import wraps
import logging
import time


class CallLimitExceededError(RuntimeError):
    """Exception raised when call limit is exceeded for a choked action."""


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

    def choke(self, window_length, limit, name=None):
        """Create a factory for producing "choked" callables.

        The choked callables implement automated registering timestamps when they are called
        and enforcing limits placed on the number of calls in defined time window.
        """
        def _choked_action_factory(target):
            tag = name or target.__name__
            logger = logging.getLogger(f'redis_choke.{tag}')
            @wraps(target)
            def _choked_action(*args, **kwargs):
                logger.debug("Getting records' count.")
                count = self.count_records(tag, window_length, prune=True)
                if count >= limit:
                    logger.debug('Call limit exceeded. Callable choked.')
                    raise CallLimitExceededError(f'Limit exceeded for callable {tag}.')
                logger.debug('Limit not exceeded (%d/%d calls in current time window)', count, limit)
                self.register_timestamp(tag)
                logger.debug('Forwarding call to wrapped callable.')
                return target(*args, **kwargs)
            return _choked_action
        return _choked_action_factory

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
