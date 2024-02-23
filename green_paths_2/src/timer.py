""" Decorator to log the time taken by a function to execute """

import time
from green_paths_2.src.logging import setup_logger, LoggerColors

LOG = setup_logger(__name__, LoggerColors.CYAN.value)


# this should be used as a decorator for functions
# e.g. @time_logger
def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours > 0:
            time_str = f"{int(hours)}h {int(minutes)}min {int(seconds)}s"
        elif minutes > 0:
            time_str = f"{int(minutes)}min {int(seconds)}s"
        else:
            time_str = f"{int(seconds)}s"

        LOG.info(f"Function {func.__name__} took {time_str} to complete")
        return result

    return wrapper
