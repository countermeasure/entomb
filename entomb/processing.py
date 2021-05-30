import contextlib
import datetime
import json
import os
import shutil
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
    utilities.print_errors(errors)


def _check_data_files(path, is_immutable):
    # Check that data files exist and are correct for an immutable file, and
    # don't exist for a mutable file.
    data_file_paths = _get_data_file_paths(path)
    if is_immutable:
        for data_file_path in data_file_paths:
            with open(data_file_path, "r") as _file:
                contents = _file.read()
            checksum_time = json.loads(contents)["checksum_time"]
            expected_contents = utilities.build_data_file_contents(
                path,
                checksum_time,
            )
            if contents != expected_contents:
                print(contents)
                print(expected_contents)
                raise Exception("")  # TODO: What sort / what message?
    else:
        data_file_directory = os.path.dirname(data_file_paths[0])
        if os.path.exists(data_file_directory):
            raise Exception("")  # TODO: What sort / what message?


def _create_data_files(path):
    """Create multiple redundant data files for the file path.

    Parameters
    ----------
    path : str
        The absolute path of the file to create data files for.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the path is not a file or does not exist.

    """
    # Parameter check.
    assert os.path.isfile(path)
    assert not os.path.islink(path)

    # Ensure the data file directory exists.
    file_directory, filename = os.path.split(path)
    data_subdirectory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY_NAME,
        constants.DATA_DIRECTORY_NAME,
        filename,
    )
    os.makedirs(data_subdirectory_path, exist_ok=True)

    # Check that no data files already exist.
    existing_files = os.listdir(data_subdirectory_path)
    if existing_files:
        raise Exception  # TODO: What sort and with what information?

    # Get data file paths.
    data_file_paths = _get_data_file_paths(path)

    # Create data file contents.
    data_file_contents = utilities.build_data_file_contents(path)

    # Create each data file.
    for data_file_path in data_file_paths:

        # Create the data file.
        with open(data_file_path, "w") as _file:
            _file.write(data_file_contents)
            # TODO: Profile without the next two lines.
            _file.flush()
            os.fsync(_file.fileno())

        # Make the data file read-only and immutable.
        os.chmod(data_file_path, 0o444)
        _set_attribute(constants.IMMUTABLE_ATTRIBUTE, data_file_path)


def _delete_directory_if_empty(path):
    """Delete an entomb directory or sub-directory if it is empty.

    If the directory is not empty, do nothing.

    Parameters
    ----------
    path : str
        An absolute path which is a directory.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the path is not a directory or is not an entomb directory or is not
        in an entomb directory or does not exist.

    """
    # Parameter check.
    assert os.path.isdir(path)
    assert _is_entomb_directory(path) or _is_entomb_subdirectory(path)

    # Delete the directory if it is empty.
    with contextlib.suppress(OSError):
        os.rmdir(path)


def _delete_data_directory(path):
    """Delete all data files for the file path.

    Directories which deleting the data files leaves empty are deleted as well.

    Parameters
    ----------
    path : str
        The absolute path of the file whose data files will be deleted.

    Returns
    -------
    None

    Raises
    ------
    AssertionError
        If the path is not a file or does not exist.

    """
    # Parameter check.
    assert os.path.isfile(path)
    assert not os.path.islink(path)

    # Get data directory path.
    file_directory, filename = os.path.split(path)
    entomb_directory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY_NAME,
    )
    data_directory_path = os.path.join(
        entomb_directory_path,
        constants.DATA_DIRECTORY_NAME,
    )
    file_data_directory_path = os.path.join(data_directory_path, filename)

    # Make all files in data directory mutable.
    for root_dir, _, filenames in os.walk(file_data_directory_path):
        for filename in filenames:
            file_path = os.path.join(root_dir, filename)
            _set_attribute(constants.MUTABLE_ATTRIBUTE, file_path)

    # Delete the data subdirectory if it's now empty.
    shutil.rmtree(file_data_directory_path)

    # Delete the .entomb/data directory if it's now empty.
    _delete_directory_if_empty(data_directory_path)

    # Delete the .entomb directory if it's now empty.
    _delete_directory_if_empty(entomb_directory_path)


def _get_data_file_paths(path):
    """Get data file paths for the file path.

    Parameters
    ----------
    path : str
        The absolute path of the file to get data file paths for.

    Returns
    -------
    list of str
        The list of data file paths for the file path.

    Raises
    ------
    AssertionError
        If the path is not a file or does not exist.

    """
    # Parameter check.
    assert os.path.isfile(path)
    assert not os.path.islink(path)

    file_directory, filename = os.path.split(path)

    # Build data file names.
    suffixes = range(1, constants.DATA_FILES_PER_FILE + 1)
    data_file_names = [
        "{}.data.{}".format(filename, suffix) for suffix in suffixes
    ]

    # Build data directory path.
    data_directory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY_NAME,
        constants.DATA_DIRECTORY_NAME,
        filename,
    )

    return [os.path.join(data_directory_path, fn) for fn in data_file_names]


def _is_entomb_directory(path):
    """Check that a directory is an entomb directory.

    Parameters
    ----------
    path : str
        An absolute path which is a directory.

    Returns
    -------
    bool
        Whether the directory is an entomb directory.

    Raises
    ------
    AssertionError
        If the path is not a directory or does not exist.

    """
    # Parameter check.
    assert os.path.isdir(path)

    return os.path.basename(path) == constants.ENTOMB_DIRECTORY_NAME


def _is_entomb_subdirectory(path):
    """Check that a path an entomb subdirectory.

    Parameters
    ----------
    path : str
        An absolute path which is a directory.

    Returns
    -------
    bool
        Whether the directory is an entomb subdirectory.

    Raises
    ------
    AssertionError
        If the path is not a directory or does not exist.

    """
    # Parameter check.
    assert os.path.isdir(path)

    subdirectory_fragment = "/{}/".format(constants.ENTOMB_DIRECTORY_NAME)

    # The path must contain "/.entomb/".
    return subdirectory_fragment in path


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

    # Find out if the file is currently immutable.
    try:
        is_immutable = utilities.file_is_immutable(path)
    except exceptions.GetAttributeError as error:
        msg = "Immutable attribute not settable for {}".format(path)
        raise exceptions.SetAttributeError(msg) from error

    # Make sure that the state (or absence) of data files related to the file
    # is correct.
    _check_data_files(path, is_immutable)

    # Work out whether to change the file's immutability.
    change_attribute = immutable != is_immutable

    # Entomb or unentomb the file if required.
    if change_attribute and not dry_run:
        if immutable:
            _set_attribute(constants.IMMUTABLE_ATTRIBUTE, path)
            _create_data_files(path)
            _write_to_log(constants.ADDED, path)
        else:
            _set_attribute(constants.MUTABLE_ATTRIBUTE, path)
            _delete_data_directory(path)
            _write_to_log(constants.REMOVED, path)

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
    except subprocess.CalledProcessError as error:
        msg = "Immutable attribute not settable for {}".format(path)
        raise exceptions.SetAttributeError(msg) from error


def _write_to_log(action, path):
    """Record an action in a log file.

    Parameters
    ----------
    action : str
        The action which was performed. Either "ADDED" or "REMOVED".
    path : str
        The absolute path of the file the action was performed upon.

    Returns
    -------
    None

    """
    file_directory, filename = os.path.split(path)

    # Ensure logs directory exists.
    logs_directory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY_NAME,
        constants.LOGS_DIRECTORY_NAME,
    )
    os.makedirs(logs_directory_path, exist_ok=True)

    # Build the log entry.
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now.strftime(constants.DATETIME_FORMAT)
    log_entry = "{} | {} | {}\n".format(timestamp, action, filename)

    # Build the log file path.
    filename_timestamp = now.strftime("%Y%m%d")
    log_filename = "entomb_{}.log".format(filename_timestamp)
    log_file_path = os.path.join(logs_directory_path, log_filename)

    # TODO: Should the log file be read-only and immutable when not being
    # written to? Yes, but profile this to see if it's worth it.

    # Append the entry to the log file.
    with open(log_file_path, "a") as _file:
        _file.write(log_entry)
        # TODO: Profile without the next two lines.
        _file.flush()
        os.fsync(_file.fileno())
