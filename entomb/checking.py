import datetime
import json
import math
import os

from entomb import (
    constants,
    utilities,
)


@utilities.hide_cursor()
def check_files(path, include_git):
    """TODO.

    Parameters
    ----------
    path : str
        An absolute path.
    include_git: bool
        Whether to include git files and directories.

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
    directory_count = 0
    entombed_file_count = 0
    errors = []
    files_with_errors_count = 0
    inaccessible_file_count = 0
    link_count = 0
    unentombed_file_count = 0

    # Print the operation.
    print("Check all files")
    print()

    # If the path is not a directory, print an abbreviated report then return.
    if not os.path.isdir(path):
        # TODO: Make this work.
        # _print_abbreviated_report(path)
        return

    # Print the progress header and set up the progress bar.
    # TODO: Get the progress bar working, and counting files correctly.
    utilities.print_header("Progress")
    total_file_paths = utilities.count_file_paths(path, include_git)
    start_time = datetime.datetime.now()
    utilities.print_progress_bar(start_time, 0, total_file_paths)

    # Walk the tree.
    for root_dir, dirnames, filenames in os.walk(path):

        # Exclude git files and directories if directed.
        if not include_git:
            dirnames[:] = [d for d in dirnames if d != ".git"]

        # Get all hash file subdirectories.
        if constants.ENTOMB_DIRECTORY_NAME in dirnames:
            data_directory = os.path.join(
                root_dir,
                constants.ENTOMB_DIRECTORY_NAME,
                constants.HASHES_DIRECTORY_NAME,
            )
            data_directory_subdirectories = os.listdir(data_directory)
        else:
            data_directory_subdirectories = []

        # Exclude data files and directories.
        dirnames[:] = [
            d for d in dirnames if d != constants.ENTOMB_DIRECTORY_NAME
        ]

        # Count the directory.
        directory_count += 1

        # Find any hash subdirectories which don't correspond to a file and
        # create errors for them.
        hash_diretories_without_files = [
            s for s in data_directory_subdirectories if s not in filenames
        ]
        for hash_directory in hash_diretories_without_files:
            hash_directory_path = os.path.join(
                root_dir,
                constants.ENTOMB_DIRECTORY_NAME,
                constants.HASHES_DIRECTORY_NAME,
                hash_directory,
            )
            msg = "{} has no corresponding file.".format(hash_directory_path)
            errors.append(msg)

        # Examine each file path.
        for filename in filenames:
            file_path = os.path.join(root_dir, filename)

            # Count the link.
            if os.path.islink(file_path):
                link_count += 1

            # Count the file.
            else:
                # Does it had a corresponding hash directory?
                has_hash_directory = filename in data_directory_subdirectories

                # Is it immutable?
                is_immutable = utilities.file_is_immutable(file_path)

                # If it's mutable and has a hash directory, that's an error.
                if has_hash_directory and not is_immutable:
                    msg = "{} should be immutable but isn't.".format(file_path)
                    errors.append(msg)
                    files_with_errors_count += 1

                # If it's immutable and doesn't have a hash directory, that's
                # an error.
                elif is_immutable and not has_hash_directory:
                    msg = (
                        "{} is immutable but doesn't have a hash directory."
                        .format(file_path)
                    )
                    errors.append(msg)
                    files_with_errors_count += 1

                # Files that have been entombed.
                elif is_immutable and has_hash_directory:
                    contents_are_okay = _hash_files_are_okay(file_path)
                    if contents_are_okay:
                        entombed_file_count += 1
                    else:
                        errors.append("TODO {}".format(file_path))
                        files_with_errors_count += 1

                # All that's left are unentombed files.
                else:
                    unentombed_file_count += 1

            total_count = (
                entombed_file_count
                + files_with_errors_count
                + inaccessible_file_count
                + link_count
                + unentombed_file_count
            )

            utilities.print_progress_bar(
                start_time,
                total_count,
                total_file_paths,
                10,
            )
    print()
    print()

    # If there are errors, write them to a log file. This will be useful if
    # there are a lot of them, because you don't want to show them all in the
    # terminal.
    _print_full_report(
        directory_count,
        entombed_file_count,
        errors,
        files_with_errors_count,
        inaccessible_file_count,
        link_count,
        unentombed_file_count,
    )


def _print_full_report(directory_count, entombed_file_count, errors,
                       files_with_errors_count, inaccessible_file_count,
                       link_count, unentombed_file_count):
    """Print a report for a path which is a file or a link.

    Parameters
    ----------
    directory_count : int
        The number of directories counted.
    link_count : int
        The number of links counted.
    immutable_file_count : int
        The number of immutable files counted.
    inaccessible_file_count : int
        The number of files for which the immutability attribute could not be
        accessed.
    mutable_file_count : int
        The number of mutable files counted.

    Returns
    -------
    None

    """
    # Do calculations.
    subdirectory_count = directory_count - 1
    total_file_count = (
        entombed_file_count
        + files_with_errors_count
        + inaccessible_file_count
        + unentombed_file_count
    )

    try:
        entombed_proportion = entombed_file_count / total_file_count
        entombed_percentage_integer = math.floor(entombed_proportion * 100)
        entombed_percentage = "{}%".format(entombed_percentage_integer)
    except ZeroDivisionError:
        entombed_percentage = "n/a"

    # Print the report.
    utilities.print_report_line("Results")
    utilities.print_report_line("Errors", utilities.stringify_int(len(errors)))
    utilities.print_report_line("Entombed", entombed_percentage)
    if unentombed_file_count:
        utilities.print_report_line(
            "Unentombed files",
            utilities.stringify_int(unentombed_file_count),
        )
    if inaccessible_file_count:
        utilities.print_report_line(
            "Inaccessible files",
            utilities.stringify_int(inaccessible_file_count),
        )
    utilities.print_report_line(
        "Total files",
        utilities.stringify_int(total_file_count),
    )
    if link_count:
        utilities.print_report_line(
            "Links",
            utilities.stringify_int(link_count),
        )
    if subdirectory_count:
        utilities.print_report_line(
            "Sub-directories",
            utilities.stringify_int(subdirectory_count),
        )
    print()

    # Print any errors.
    utilities.print_errors(errors)


def _hash_files_are_okay(file_path):
    # TODO: Put the next line in a try/except block.
    actual_contents = _get_hash_file_contents(file_path)
    hash_time = json.loads(actual_contents)["hash_time"]
    expected_contents = utilities.build_hash_file_contents(
        file_path,
        hash_time,
    )
    # Check that actual and expected contents match.
    if actual_contents != expected_contents:
        return False

    # Check that all data files are immutable and read-only.
    file_directory, filename = os.path.split(file_path)
    hash_directory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY_NAME,
        constants.HASHES_DIRECTORY_NAME,
        filename,
    )
    hash_file_names = os.listdir(hash_directory_path)
    for hash_file_name in hash_file_names:
        hash_file_path = os.path.join(hash_directory_path, hash_file_name)
        is_immutable = utilities.file_is_immutable(hash_file_path)
        statinfo = os.stat(hash_file_path)
        # TODO: Make utilities.file_is_read_only(path) function.
        is_read_only = oct(statinfo.st_mode).endswith("444")
        if not is_immutable or not is_read_only:
            return False

    return True


def _get_hash_file_contents(path):
    # Parameter check.
    assert os.path.isfile(path)
    assert not os.path.islink(path)

    file_directory, filename = os.path.split(path)
    hash_directory_path = os.path.join(
        file_directory,
        constants.ENTOMB_DIRECTORY_NAME,
        constants.HASHES_DIRECTORY_NAME,
        filename,
    )
    hash_file_names = os.listdir(hash_directory_path)
    hashes = set()

    for hash_file_name in hash_file_names:
        hash_file_path = os.path.join(hash_directory_path, hash_file_name)
        with open(hash_file_path, "r") as _file:
            contents = _file.read()
            hashes.add(contents)
    hashes_count = len(hashes)
    if hashes_count == 1:
        return list(hashes)[0]
    if hashes_count == 0:
        raise Exception("TODO: There are no hashes")
    if hashes_count > 1:
        raise Exception("TODO: There are multiple hashes")
