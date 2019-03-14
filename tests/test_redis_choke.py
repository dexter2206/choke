"""Test cases for redis_choke module."""
from itertools import chain, repeat
import pytest
from choke.redis_choke import RedisChokeManager


def test_calls_zadd(mocker):
    """RedisChokeManager should call zadd of its redis object when registering timestamp."""
    redis_mock = mocker.Mock()
    time_mock = mocker.Mock(return_value=100.0)
    choke = RedisChokeManager(redis_mock, time_source=time_mock)

    choke.register_timestamp('test_tag')

    redis_mock.zadd.assert_called_once_with('test_tag', {100.0: 100.0})

def test_calls_zremrangebyscore(mocker):
    """RedisChokeManager should call redis.zremrangebyscore when pruning timestamps."""
    redis_mock = mocker.Mock()
    time_mock = mocker.Mock(return_value=100)
    choke = RedisChokeManager(redis_mock, time_source=time_mock)

    choke.prune('some_tag', 1000, ref_timestamp=4120.0)

    redis_mock.zremrangebyscore.assert_called_once_with('some_tag', 0, 3120.0)

def test_obtains_reference_timestamp(mocker):
    """RedisChokeManager should use its time_source to obtain reference timestamp when pruning."""
    redis_mock = mocker.Mock()
    time_mock = mocker.Mock(return_value=2137.0)
    choke = RedisChokeManager(redis_mock, time_source=time_mock)

    choke.prune('some_tag', 1000)
    time_mock.assert_called_once_with()
    redis_mock.zremrangebyscore.assert_called_once_with('some_tag', 0, 1137.0)

def test_calls_zcount(mocker):
    """RedisChokeManager should call redis.zcount for obtaining count of timestamps."""
    redis_mock = mocker.Mock()
    redis_mock.zcount.return_value = 31
    time_mock = mocker.Mock(return_value=6415.0)
    choke = RedisChokeManager(redis_mock, time_source=time_mock)

    assert choke.count_records('tag123', 27) == 31
    redis_mock.zcount.assert_called_once_with('tag123', '(6388.0', 6415.0)
