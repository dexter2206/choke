"""Test cases for simple_choke module."""
from itertools import chain, repeat
import pytest
from choke.simple_choke import SimpleChokeManager


def test_registers_timestamp(mocker):
    """SimpleChokeManager should correctly register timestamps."""
    time = mocker.Mock(side_effect=[10, 100, 190])
    choke_manager = SimpleChokeManager(time_source=time)

    for _ in range(3):
        choke_manager.register_timestamp('mytag')

    assert choke_manager.get_records('mytag') == (10, 100, 190)

def test_prune(mocker):
    """SimpleChokeManager should prune records using current time and provided window_length."""
    time = mocker.Mock(side_effect=[100, 250, 300, 350, 400, 450, 450])
    choke_manager = SimpleChokeManager(time_source=time)

    for _ in range(4):
        choke_manager.register_timestamp('mytag')

    choke_manager.prune('mytag', window_length=200)
    assert choke_manager.get_records('mytag') == (250, 300, 350)
    choke_manager.prune('mytag', window_length=200)
    assert choke_manager.get_records('mytag') == (300, 350)
    choke_manager.prune('mytag', window_length=150)
    assert choke_manager.get_records('mytag') == (350,)

@pytest.mark.parametrize(
    'timestamps, window_length, exp_count',
    [
        [[21, 37, 39, 43], 80, 3],
        [[21, 37, 39, 43], 7, 2],
        [[21, 37, 39, 43], 6, 1],
        [[21, 37, 39, 43], 3, 0]
    ])
def test_count_noprune(timestamps, window_length, exp_count, mocker):
    """SimpleChokeManager should correctly count registered timestamps wnen prune=False."""
    time = mocker.Mock(side_effect=timestamps)
    choke_manager = SimpleChokeManager(time_source=time)

    for _ in range(len(timestamps)-1):
        choke_manager.register_timestamp('mytag')

    assert choke_manager.count_records('mytag', window_length, prune=False) == exp_count

def test_count_prune(mocker):
    """SimpleChokeManager should correctly count registered timestamps wnen prune=True."""
    time = mocker.Mock(side_effect=chain([100, 200, 300, 400], repeat(401)))
    choke_manager = SimpleChokeManager(time_source=time)

    for _ in range(4):
        choke_manager.register_timestamp('mytag')

    assert choke_manager.count_records('mytag', window_length=400) == 4
    assert choke_manager.count_records('mytag', window_length=200) == 2

    # After pruning this value should change
    assert choke_manager.count_records('mytag', window_length=400) == 2
