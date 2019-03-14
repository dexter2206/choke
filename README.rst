choke: simple implementation of throttling mechanism
====================================================

|License: MIT| |Build Status|

**choke** is a package implementing a trivial to use general purpose throttling mechanism. The basic workflow with **choke** is as follows:

1. Create manager - an object responsible for keeping track of timestamps when some events (think: calls to your functions) occur.
2. Instruct manager to "choke" some callables, i.e. define maximum number of calls that can occur per given time window.
3. Use your callables as usual, keeping in mind that when the above defined limit is exceeded, the choked callable will raise `CallLimitExceededError`.

Here is an example containing everything you need to use **choke**:

.. code:: python

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


.. |License: MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
.. |Build Status| image:: https://travis-ci.org/dexter2206/choke.svg?branch=master
   :target: https://travis-ci.org/dexter2206/choke
