import contextlib
import datetime
import hashlib
import json
import os
import subprocess

from entomb import (
    constants,
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


def _create_data_files(path):
    """TODO.

    """
    # TODO: Write tests for this function.
    # Create data file contents.
    now = datetime.datetime.now().astimezone()
    sha512_hash = _get_sha512_hash(path)
    data = {
        "hash": "sha512-{}".format(sha512_hash),
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    data_file_paths = _get_data_file_paths(path)

    for data_file_path in data_file_paths:

        # Ensure the data file directory exists.
        data_file_directory = os.path.dirname(data_file_path)
        os.makedirs(data_file_directory, exist_ok=True)

        # Write the data file.
        with open(data_file_path, "w") as f:
            f.write(json.dumps(data, indent=4))

        # Make the data file read-only and immutable.
        os.chmod(data_file_path, 0o444)
        _set_attribute(constants.IMMUTABLE_ATTRIBUTE, data_file_path)


def _delete_data_file(path):
    """TODO.

    """
    # TODO: Write tests for this function.
    # Check that the path contains "/.entomb/" or it's not in an entomb
    # directory.
    is_in_entomb_directory = "/{}/".format(constants.ENTOMB_DIRECTORY) in path
    assert is_in_entomb_directory

    os.remove(path)


def _delete_directory_if_empty(directory):
    """TODO.

    """
    # TODO: Write tests for this function.
    # Check that the path contains "/.entomb/" or ends with "/.entomb", or it's
    # not an entomb directory.
    is_entomb_directory = any([
        "/{}/".format(constants.ENTOMB_DIRECTORY) in directory,
        directory.endswith("/{}".format(constants.ENTOMB_DIRECTORY)),
    ])
    assert is_entomb_directory

    # Delete the directory if it is empty.
    with contextlib.suppress(OSError):
        os.rmdir(directory)


def _get_data_file_paths(path):
    """TODO.

    """
    # TODO: Write tests for this function.
    file_directory, filename = os.path.split(path)

    # Build data file names.
    suffixes = range(1, constants.DATA_FILES_PER_FILE + 1)
    data_file_names = [
        "{}.data.{}".format(filename, suffix) for suffix in suffixes
    ]

    # Build data file paths.
    entomb_directory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY,
    )
    data_directory_path = os.path.join(entomb_directory_path, "data", filename)
    data_file_paths = [
        os.path.join(data_directory_path, fn) for fn in data_file_names
    ]

    return data_file_paths


def _delete_data_files(path):
    """TODO.

    """
    # TODO: Write tests for this function.
    data_file_paths = _get_data_file_paths(path)

    for data_file_path in data_file_paths:

        # Make the data file mutable so it can be deleted.
        _set_attribute(constants.MUTABLE_ATTRIBUTE, data_file_path)

        _delete_data_file(data_file_path)

    # Delete the data files directory.
    data_file_directory = os.path.dirname(data_file_path)
    _delete_directory_if_empty(data_file_directory)

    # Delete the .entomb/data directory if it's now empty.
    data_directory = os.path.dirname(data_file_directory)
    _delete_directory_if_empty(data_directory)

    # Delete the .entomb directory if it's now empty.
    entomb_directory = os.path.dirname(data_directory)
    _delete_directory_if_empty(entomb_directory)


def _get_sha512_hash(path):
    """TODO.

    Parameters
    ----------
    path : str
        The absolute path of a file.

    Returns
    -------
    str
        The sha512 hash of the file at the path.

    """
    # TODO: Write tests for this function.
    sha512 = hashlib.sha512()
    chunk_size = 16384

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha512.update(chunk)

    return sha512.hexdigest()


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
        if immutable:
            _set_attribute(constants.IMMUTABLE_ATTRIBUTE, path)
            _create_data_files(path)
        else:
            _set_attribute(constants.MUTABLE_ATTRIBUTE, path)
            _delete_data_files(path)

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
