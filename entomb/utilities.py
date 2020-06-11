import datetime
import decimal
import os
import subprocess
from contextlib import contextmanager

from entomb import (
    constants,
    exceptions,
)


def clear_line():
    """Clear the current line in the terminal.

    Returns
    -------
    None

    """
    print("\033[K", end="")


def count_file_paths(path, include_git, print_frequency=1000):
    """Count the file paths in a directory.

    Prints the file path count as it progresses.

    Parameters
    ----------
    path : str
        An absolute path.
    include_git: bool
        Whether to include git files.
    print_frequency : int, optional
        The number of file paths to count before re-printing the count. The
        default is 1000.

    Returns
    -------
    int
        The number of file paths in the directory and its subdirectories.

    Raises
    ------
    ObjectTypeError
        If the path's object is not a directory.
    PathDoesNotExistError
        If the path does not exist.

    """
    print("Counting file paths: 0", end="\r")

    count = 0

    # Walk the path.
    for _ in file_paths(path, include_git):
        count += 1

        # Only print the count at the specified frequency.
        if count % print_frequency == 0:
            print("Counting file paths: {:,}".format(count), end="\r")

    # Clear the final count message.
    clear_line()

    return count


def file_is_immutable(path):
    """Whether a file has the immutable attribute set.

    Parameters
    ----------
    path : str
        An absolute path.

    Returns
    -------
    bool
        True if the file's immmutable attribute is set, False if it is not.

    Raises
    ------
    ObjectTypeError
        If the path's object is not a file.
    PathDoesNotExistError
        If the path does not exist.
    ProcessingError
        If the exit status of the lsattr command is non-zero.

    """
    # Raise an exception if the path does not exist.
    if not os.path.exists(path):
        msg = "'lsattr' received '{}' which is not a path".format(path)
        raise exceptions.PathDoesNotExistError(msg)

    # Raise an exception if the path is to a link.
    if os.path.islink(path):
        msg = "'lsattr' requires a file, but '{}' is a link".format(path)
        raise exceptions.ObjectTypeError(msg)

    # Raise an exception if the path is to a directory.
    if os.path.isdir(path):
        msg_template = "'lsattr' requires a file, but '{}' is a directory"
        msg = msg_template.format(path)
        raise exceptions.ObjectTypeError(msg)

    # Get the immutable flag.
    immutable_flag = _get_immutable_flag(path)

    return immutable_flag == "i"


def file_paths(path, include_git):
    """Generate paths of all files and links on the path.

    Parameters
    ----------
    path : str
        An absolute path.
    include_git: bool
        Whether to include git files.

    Yields
    ------
    str
        An absolute path.

    Raises
    ------
    PathDoesNotExistError
        If the path does not exist.

    """
    # Raise an exception if the path does not exist. Note that this exception
    # appears to only be raised when the generator is iterated, not when it is
    # created.
    if not os.path.exists(path):
        msg = "The path '{}' does not exist".format(path)
        raise exceptions.PathDoesNotExistError(msg)

    # Yield the path if the path is to a file or link.
    if os.path.isfile(path):
        yield path

    # Walk the path if the path is to a directory.
    for root_dir, dirnames, filenames in os.walk(path):

        # Exclude git files and directories if directed.
        if not include_git:
            dirnames[:] = [d for d in dirnames if d != ".git"]

        for filename in filenames:
            yield os.path.join(root_dir, filename)


@contextmanager
def hide_cursor():
    """Hide the cursor and then finally show it again.

    Used as a decorator to hide the cursor when a function starts and
    show the cursor again when the function finishes or an exception occurs.

    Yields
    ------
    None

    """
    # Hide the cursor.
    print("\033[?25l", end="")
    try:
        yield
    finally:
        # Show the cursor.
        print("\033[?25h", end="")


def print_header(header):
    """Print a underlined header.

    Parameters
    ----------
    header : str
        The header text.

    Returns
    -------
    None

    """
    print(header)
    print("-" * len(header))


def print_progress_bar(start_time, count, total, print_frequency=100):
    """Print a progress bar.

    Parameters
    ----------
    start_time : datetime
        When the operation being reported on began.
    count : int
        The number of cycles completed.
    total : int
        The total number of cycles to complete.
    print_frequency : int, optional
        The number of cycles to complete before re-printing the count. The
        default is 100.

    Returns
    -------
    None

    """
    # Print the progress bar at the specified frequency or when the operation
    # is finished.
    is_finished = count == total
    update_now = count % print_frequency == 0

    if is_finished or update_now:

        # Build the progress bar.
        progress_bar = _build_progress_bar(count, total)
        progress_bar = _add_percentage_to_progress_bar(
            progress_bar,
            count,
            total,
        )
        progress_bar = _add_time_to_progress_bar(
            progress_bar,
            start_time,
            count,
            total,
        )

        # Print the progress bar.
        clear_line()
        print(progress_bar, end="\r")


def _add_percentage_to_progress_bar(progress_bar, count, total):
    """Add the percentage to the progress bar.

    Parameters
    ----------
    progress_bar : str
        The bar component of the progress bar, as built so far.
    count : int
        The number of cycles completed.
    total : int
        The total number of cycles to complete.

    Returns
    -------
    str
        The progress bar, with percentage appended if appropriate.

    """
    operation_is_not_finished = count != total

    if operation_is_not_finished:
        progress = count / total if total > 0 else 1
        percentage = progress * 100
        # Round the percentage down so that it is never shown as 100% before
        # the operation is finished.
        rounded_percentage = decimal.Decimal(percentage).quantize(
            decimal.Decimal("0.0"), rounding=decimal.ROUND_DOWN,
        )
        progress_bar += "  {}%".format(rounded_percentage)

    return progress_bar


def _add_time_to_progress_bar(progress_bar, start_time, count, total):
    """Add the time remaining to the progress bar.

    Parameters
    ----------
    progress_bar : str
        The bar component of the progress bar, as built so far.
    start_time : datetime
        When the operation being reported on began.
    count : int
        The number of cycles completed.
    total : int
        The total number of cycles to complete.

    Returns
    -------
    str
        The progress bar, with time remaining appended if appropriate.

    """
    operation_is_not_finished = count != total
    time_elapsed = datetime.datetime.now() - start_time
    seconds_elapsed = time_elapsed.total_seconds()
    show_time_remaining = seconds_elapsed > 2 and operation_is_not_finished

    if show_time_remaining:
        rate = count / seconds_elapsed
        seconds_remaining = (total - count) / rate
        time_remaining = _readable_duration(seconds_remaining)
        progress_bar += "  |  {} to go".format(time_remaining)

    return progress_bar


def _build_progress_bar(count, total):
    """Build the bar component of the progress bar.

    Parameters
    ----------
    count : int
        The number of cycles completed.
    total : int
        The total number of cycles to complete.

    Returns
    -------
    str
        The bar component of the progress bar.

    """
    # If total is 0, the operation has nothing to do, so it is complete.
    progress = count / total if total != 0 else 1
    bar_width = constants.TABLE_WIDTH
    progress_width = int(progress * bar_width)

    return ("█" * progress_width).ljust(bar_width, "░")


def _get_immutable_flag(path):
    """Get the immutable flag of a file.

    This function assumes that the path has already been confirmed to reference
    a file.

    Parameters
    ----------
    path : str
        An absolute path to a file.

    Returns
    -------
    str
        The string "i" if the file is immutable, or "-" if it is not.

    Raises
    ------
    ProcessingError
        If the exit status of the lsattr command is non-zero.

    """
    try:
        lsattr_result = subprocess.run(
            ["lsattr", path],
            check=True,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError:
        msg = "'lsattr' failed for '{}'".format(path)
        raise exceptions.ProcessingError(msg)

    # Extract the immutable attribute from the command output.
    attributes = lsattr_result.stdout.split()[0]
    immutable_flag = list(attributes)[4]

    return immutable_flag


def _readable_duration(duration):
    """Convert a duration in seconds to a human-readable duration.

    Parameters
    ----------
    duration : int
        A duration in seconds.

    Returns
    -------
    str
        A human-readable duration.

    """
    rounded_duration = round(duration)

    if rounded_duration < 60:
        duration_string = "{}s".format(rounded_duration)
    elif rounded_duration < 60 * 60:
        minutes, seconds = divmod(rounded_duration, 60)
        duration_string = "{}m {:02d}s".format(minutes, seconds)
    else:
        total_minutes, seconds = divmod(rounded_duration, 60)
        hours, minutes = divmod(total_minutes, 60)
        duration_string = (
            "{:,}h {:02d}m {:02d}s".format(hours, minutes, seconds)
        )

    return duration_string
