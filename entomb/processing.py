import os
import subprocess

from entomb import (
    exceptions,
    utilities,
)


def process_objects(path, immutable, include_git, dry_run):
    """Set or unset the immutable attribute for all files on a path.

    Parameters
    ----------
    path : str
        An absolute path.
    immutable: bool
        Set immutable attributes if True, unset immutable attributes if False.
    include_git: bool
        Whether to include git files and directories.
    dry_run: bool
        Whether to do a dry run which makes no changes.

    Returns
    -------
    None

    """
    # Set up.
    attribute_changed_count = 0
    errors = []
    file_count = 0
    link_count = 0
    operation = "entombed" if immutable else "unset"
    operation_message = "Entomb objects" if immutable else "Unset objects"

    # Print the operation.
    print(operation_message)
    print()

    # Print the progress header and first progress message.
    utilities.print_header("Progress")
    print("-", end="\r")

    # Walk the tree.
    for file_path in utilities.file_paths(path, include_git):

        # Count links, but don't try to operate on them as they don't have
        # an immutable attribute.
        if os.path.islink(file_path):
            link_count += 1

        else:
            # Work out if the file's attribute needs to change.
            is_immutable = utilities.file_is_immutable(file_path)
            change_attribute = immutable != is_immutable

            # Change the file's attribute if necessary.
            if change_attribute and not dry_run:
                try:
                    _process_object(file_path, immutable)
                except exceptions.ObjectTypeError as exception:
                    errors.append(exception)
                except exceptions.ProcessingError as exception:
                    errors.append(exception)

            # Count the file.
            file_count += 1
            if change_attribute:
                attribute_changed_count += 1

        # Update the progress message.
        progress = "{} {} of {} files and ignored {} links".format(
            operation.title(),
            attribute_changed_count,
            file_count,
            link_count,
        )
        print(progress, end="\r")

    print()
    print()

    # Print the changes.
    if file_count > 0:
        utilities.print_header("Changes")
        print("{} {} files".format(operation.title(), attribute_changed_count))
        print()

    # Print a summary.
    utilities.print_header("Summary")
    if file_count > 0:
        print("All {} files are now {}".format(file_count, operation))
        print("All {} links were ignored".format(link_count))
    else:
        print("No files were found")
    print()

    # Print any errors.
    _print_errors(errors)


def _print_errors(errors):
    """Print the list of errors resulting from file processing.

    Parameters
    ----------
    errors : list of str
        A list of error messages.

    Returns
    -------
    None

    """
    # Return if there are no errors.
    if not errors:
        return

    # Print the header.
    utilities.print_header("Errors")

    # Print up to 10 errors.
    for error in errors[:10]:
        print(">> {}".format(error))

    # If there are more than 10 errors, print a message about how many more
    # there are.
    error_count = len(errors)
    if error_count > 10:
        unshown_errors = len(errors) - 10
        print(">> Plus {} more errors".format(unshown_errors))

    print()


def _process_object(path, immutable):
    """Set or unset the immutable attribute for a file.

    Parameters
    ----------
    path : str
        The absolute path of a file.
    immutable: bool
        Set immutable attribute if True, unset immutable attribute if False.

    Returns
    -------
    None

    Raises
    ------
    PathDoesNotExistError
        If the path does not exist.
    ProcessingError
        If the exit status of the chattr command is non-zero.
    ObjectTypeError
        If the path's object is not a file.

    """
    # Raise an exception if the path does not exist.
    if not os.path.exists(path):
        msg = "The path '{}' does not exist".format(path)
        raise exceptions.PathDoesNotExistError(msg)

    # Raise an exception if called with a path to a link.
    if os.path.islink(path):
        msg = "'{}' is a link, but a file is required".format(path)
        raise exceptions.ObjectTypeError(msg)

    # Raise an exception if called with a path to a directory.
    if os.path.isdir(path):
        msg = "'{}' is a directory, but a file is required".format(path)
        raise exceptions.ObjectTypeError(msg)

    attribute = "+i" if immutable else "-i"

    _set_attribute(attribute, path)


def _set_attribute(attribute, path):
    """Set or unset an attribute for a file.

    Parameters
    ----------
    attribute: str
        The attribute to be set. In the form of "+i" or "-i".
    path : str
        The absolute path of a file.

    Returns
    -------
    None

    Raises
    ------
    ProcessingError
        If the exit status of the chattr command is non-zero.

    """
    try:
        subprocess.run(
            ["sudo", "chattr", attribute, path],
            check=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        msg = "The 'chattr' command failed for '{}'".format(path)
        raise exceptions.ProcessingError(msg)
