import logging
import random
import time

logger = logging.getLogger(__name__)


def humanized_wait_duration(min_time: float, max_time: float | None = None, multiplier: float = 2) -> float:
    """Generate a humanized wait time with random variations.

    Args:
        min_time: Minimum wait time in seconds
        max_time: Maximum wait time in seconds. If None, uses min_time * multiplier
        multiplier: Multiplier for max_time when max_time is None

    Returns:
        float: The actual wait time in seconds
    """
    # Add a small random delay (0-1 seconds)
    # trunk-ignore(bandit/B311)
    small_delay = random.random()

    # Calculate the main wait time
    if max_time is None:
        max_time = min_time * multiplier

    # trunk-ignore(bandit/B311)
    main_wait = random.uniform(min_time, max_time)

    # Total wait time
    actual_wait = small_delay + main_wait

    return actual_wait


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

    time.sleep(humanized_wait_duration(min_time=min_wait, max_time=max_wait, multiplier=multiply_factor))


def duration_to_type(value: str, speed: int = 100) -> float:
    """Calculate the duration needed to type a text at a given speed.

    Args:
        value: The text to type
        speed: Typing speed in words per minute (default: 100)

    Returns:
        float: Duration in seconds needed to type the text
    """
    # Average word length is 5 characters
    avg_word_length = 5

    # Calculate number of words (roughly)
    num_words = len(value) / avg_word_length

    # Calculate time in minutes
    time_minutes = num_words / speed

    # Convert to seconds
    time_seconds = time_minutes * 60

    # Add some randomness (±20%)
    # trunk-ignore(bandit/B311)
    variation = random.uniform(0.8, 1.2)

    return time_seconds * variation
