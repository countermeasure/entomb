import os
import subprocess

from entomb import exceptions


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
