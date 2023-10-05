import random
import time


def humanized_wait(min_wait: int, max_wait: int = None, multiply_factor: float = 2, wait_addendum: float = 0.25):
    """Randomized wait (to be more human-like). Multiple calls to the function with
     the same argument still waits for a different period of time.

    - Minimum wait of `wait_addendum` is guaranteed (even if a user passes 0 wait time).
    - Additional wait of x E [0, 1] is also added (to have unpredictable wait time).
    - Actual wait is calculated based on user supplied `min wait` and other params.
    """
    max_wait = int(max_wait or min_wait * multiply_factor)
    actual_wait = wait_addendum + random.randint(min_wait, max_wait) + random.random()  # nosec
    time.sleep(actual_wait)
