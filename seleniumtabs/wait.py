import logging
import random
import time

logger = logging.getLogger(__name__)


def humanized_wait(
    min_wait: int, max_wait: int | None = None, multiply_factor: float = 2, wait_addendum: float = 0.25
) -> None:
    """Randomized wait to simulate human-like behavior.

    This function implements a randomized wait mechanism that makes automated
    browser interactions appear more human-like. Multiple calls with the same
    arguments will result in different wait times.

    The actual wait time is calculated as:
        wait_addendum + random(0,1) + random(min_wait, max_wait)

    Args:
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds. If None, calculated as min_wait * multiply_factor
        multiply_factor: Factor to multiply min_wait by when max_wait is None
        wait_addendum: Additional base wait time to ensure minimum delay

    Raises:
        ValueError: If any of the parameters are invalid

    Examples:
        >>> humanized_wait(1)  # Wait between 1.25 and 3.25 seconds
        >>> humanized_wait(2, 5)  # Wait between 2.25 and 6.25 seconds
        >>> humanized_wait(1, multiply_factor=3)  # Wait between 1.25 and 4.25 seconds
    """
    # Input validation
    if min_wait < 0:
        raise ValueError("min_wait must be non-negative")
    if max_wait is not None and max_wait < min_wait:
        raise ValueError("max_wait must be greater than or equal to min_wait")
    if multiply_factor <= 0:
        raise ValueError("multiply_factor must be positive")
    if wait_addendum < 0:
        raise ValueError("wait_addendum must be non-negative")

    # Calculate wait time
    max_wait = int(max_wait or min_wait * multiply_factor)
    actual_wait = wait_addendum + random.random() + random.randint(min_wait, max_wait)  # nosec

    # Log wait time
    logger.debug(f"Waiting for {actual_wait:.2f} seconds")

    try:
        time.sleep(actual_wait)
    except KeyboardInterrupt:
        logger.warning("Wait interrupted by user")
        raise
    except Exception as e:
        logger.error(f"Error during wait: {str(e)}")
        raise
