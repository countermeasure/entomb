import os
import sys

from entomb import utilities


def list_files(path, immutable, include_git):
    """Print a list of the immutable or mutable files on the path.

    Parameters
    ----------
    path : str
        An absolute path.
    immutable: bool
        List immutable files if True, mutable files if False.
    include_git: bool
        Whether to include git files and directories.

    Returns
    -------
    None

    """
    # Set up.
    file_count = 0
    link_count = 0
    printed_file_count = 0
    state = "immutable" if immutable else "mutable"

    # Print the operation.
    print("List {} files".format(state))
    print()

    # Print the list header.
    list_header = "{} files".format(state.title())
    utilities.print_header(list_header)

    # Walk the tree.
    for file_path in utilities.file_paths(path, include_git):

        # Count the link.
        if os.path.islink(file_path):
            link_count += 1

        # Count the file and print its path if appropriate.
        else:
            if _print_the_path(file_path, immutable):
                printed_file_count += 1
                print(file_path)

            file_count += 1

        # Update the progress message.
        progress = "Examined {} files and {} links".format(
            file_count,
            link_count,
        )
        print(progress, end="\r")

    # Clear the final progress message.
    _clear_line()

    # If the list is empty, print an empty indicator.
    if printed_file_count == 0:
        print("-")

    # Print a summary.
    print()
    utilities.print_header("Summary")
    print("{} files were examined".format(file_count))
    print("{} files are {}".format(printed_file_count, state))
    print()


def _clear_line():
    """Clear the current line in the terminal.

    Returns
    -------
    None

    """
    sys.stdout.write("\033[K")
    sys.stdout.flush()


def _print_the_path(path, immutable):
    """Determine whether to print the file path.

    The path should be printed if the immutable parameter is True and the file
    is immutable, or if the immutable parameter is False and the file is
    mutable.

    Parameters
    ----------
    path : str
        An absolute path.
    immutable: bool
        List immutable files if True, mutable files if False.

    Returns
    -------
    bool
        Whether to print the file path.

    Raises
    ------
    ProcessingError
        If the path is a link or directory.

    """
    is_immutable = utilities.file_is_immutable(path)
    print_immutable_file_path = is_immutable and immutable
    print_mutable_file_path = not is_immutable and not immutable

    return print_immutable_file_path or print_mutable_file_path
