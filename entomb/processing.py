import datetime
import os
import subprocess

from entomb import (
    exceptions,
    utilities,
)


@utilities.hide_cursor()
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

    Raises
    ------
    AssertionError
        If the path does not exist.

    """
    # Parameter check.
    assert os.path.exists(path)

    # Set up.
    attribute_changed_count = 0
    attribute_settable_count = 0
    errors = []
    file_count = 0
    link_count = 0
    operation = "entombed" if immutable else "unset"

    # Print the operation.
    if immutable:
        print("Entomb objects")
    else:
        print("Unset objects")
    print()

    # Print the progress header and set up the progress bar.
    utilities.print_header("Progress")
    total_file_paths = utilities.count_file_paths(path, include_git)
    start_time = datetime.datetime.now()
    utilities.print_progress_bar(start_time, 0, total_file_paths)

    # Walk the tree.
    for file_path in utilities.file_paths(path, include_git):

        # Count links, but don't try to operate on them as they don't have
        # an immutable attribute.
        if os.path.islink(file_path):
            link_count += 1

        else:
            # Change the file's attribute if necessary.
            try:
                attribute_was_changed = _process_object(
                    file_path,
                    immutable,
                    dry_run,
                )
                attribute_settable_count += 1
                if attribute_was_changed:
                    attribute_changed_count += 1
            except exceptions.SetAttributeError as error:
                errors.append(error)

            # Count the file.
            file_count += 1

        # Update the progress bar.
        utilities.print_progress_bar(
            start_time,
            (file_count + link_count),
            total_file_paths,
        )

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
        print(
            "All {} files for which immutability can be set are now {}"
            .format(attribute_settable_count, operation),
        )
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


def _process_object(path, immutable, dry_run):
    """Set or unset the immutable attribute for a file.

    Parameters
    ----------
    path : str
        The absolute path of a file.
    immutable: bool
        Set immutable attribute if True, unset immutable attribute if False.
    dry_run : bool
        Whether to do a dry run which makes no changes.

    Returns
    -------
    bool
        Whether the immutable attribute was changed, or if this was a dry run,
        should have been changed.

    Raises
    ------
    AssertionError
        If the path is a directory, is a link or does not exist.
    SetAttributeError
        If the path's immutable attribute cannot be set.

    """
    # Parameter check.
    assert not os.path.isdir(path)
    assert not os.path.islink(path)
    assert os.path.exists(path)

    try:
        is_immutable = utilities.file_is_immutable(path)
    except exceptions.GetAttributeError:
        msg = "Immutable attribute not settable for {}".format(path)
        raise exceptions.SetAttributeError(msg)

    change_attribute = immutable != is_immutable

    if change_attribute and not dry_run:
        attribute = "+i" if immutable else "-i"
        _set_attribute(attribute, path)

    # The value of change_attribute is a proxy for whether the immutable
    # attribute was changed, or if this was a dry run, should have been
    # changed.
    return change_attribute


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
    SetAttributeError
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
        msg = "Immutable attribute not settable for {}".format(path)
        raise exceptions.SetAttributeError(msg)
