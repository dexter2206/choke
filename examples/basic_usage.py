"""Example demonstrating a basic usage of choke package."""
from time import sleep
from redis import StrictRedis
from choke import RedisChokeManager, CallLimitExceededError


REDIS = StrictRedis() # Tweak this to reflect your setup
CHOKE_MANAGER = RedisChokeManager(redis=REDIS)

# Example configuration: enforce limit of no more than 10 calls in two seconds window
@CHOKE_MANAGER.choke(limit=10, window_length=2)
def foo(x, y):
    """Just print something to show that foo was called."""
    print(f'foo called with ({x}, {y})')

if __name__ == '__main__':
    # We expect pattern of 10 successes followed by 10 failures followed again by 10 successes
    # Some deviations from this pattern may obviously occur as calling foo takes nonzero time
    for i in range(30):
        try:
            foo(i, y=i ** 2)
        except CallLimitExceededError:
            print('Foo not called. Limit exceeded!')
        sleep(0.1)
