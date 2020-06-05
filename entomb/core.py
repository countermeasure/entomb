#!/usr/bin/env python3
import argparse
import os
import signal
import subprocess
import sys

import entomb
from entomb import (
    constants,
    exceptions,
    listing,
    processing,
    reporting,
    utilities,
)


def main(argv):
    """Run Entomb.

    Parameters
    ----------
    argv : list
        List of arguments from the command line, including the executable.

    Returns
    -------
    int
        The exit status.

    """
    # Parse the command line input.
    args = _parse_args(argv)

    # If any optional arguments conflict, print the errors and return a
    # non-zero exit status.
    argument_conflicts = _check_argument_conflicts(args)
    if argument_conflicts:
        _print_argument_conflict_errors(argument_conflicts)
        return 1

    # Get the absolute path.
    absolute_path = _get_absolute_path(args.path)

    # If the absolute path doesn't exist, print an error and return a non-zero
    # exit status.
    if not os.path.exists(absolute_path):
        _print_path_not_found_error(args.path, absolute_path)
        return 1

    # Trigger the sudo prompt if the operation can change immutability
    # attributes and the user does not currently have root priviliges.
    root_privileges_required = not any([
        args.dry_run,
        args.list_immutable,
        args.list_mutable,
        args.report,
    ])
    user_has_root_privileges = _user_has_root_privileges()
    if root_privileges_required and not user_has_root_privileges:
        _prompt_for_sudo()

    # Print the entomb header.
    print()
    print("======")
    print("Entomb")
    print("======")
    print()

    # Print the dry run message if required.
    if args.dry_run:
        print(">> This is a dry run so no changes will be made")
        print()

    # Print the include git message if required.
    if args.include_git:
        print(">> Files in .git directories are being included")
        print()

    # Print the path type header.
    path_type = _get_path_type(absolute_path)
    utilities.print_header(path_type.title())

    # Print the path.
    print(absolute_path)
    print()

    # Print the operation header.
    utilities.print_header("Operation")

    # If a report is requested, print it then return a zero exit status.
    if args.report:
        reporting.produce_report(absolute_path, include_git=args.include_git)
        return 0

    # If a list of immutable objects is requested, print it then return a zero
    # exit status.
    if args.list_immutable:
        listing.list_files(
            absolute_path,
            immutable=True,
            include_git=args.include_git,
        )
        return 0

    # If a list of mutable objects is requested, print it then return a zero
    # exit status.
    if args.list_mutable:
        listing.list_files(
            absolute_path,
            immutable=False,
            include_git=args.include_git,
        )
        return 0

    # Set the immutable attribute for everything on the path, then return a
    # zero exit status.
    processing.process_objects(
        absolute_path,
        immutable=not args.unset,
        include_git=args.include_git,
        dry_run=args.dry_run,
    )
    return 0


def run():
    """Call main() to run Entomb.

    This is the console script entry point.

    Returns
    -------
    None

    """
    # Set handler for interrupt and termination signals.
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Run Entomb, exiting with a status code when finished.
    sys.exit(main(sys.argv))


def _check_argument_conflicts(args):
    """Check whether any optional arguments conflict with each other.

    Parameters
    ----------
    args : instance of Namespace
        Parsed arguments from the command line.

    Returns
    -------
    list of str
        The list of argument conflict messages.

    """
    # Match each argument with a list of the arguments compatible with it.
    compatibility = {
        constants.DRY_RUN_ARG: [
            constants.INCLUDE_GIT_ARG,
            constants.UNSET_ARG,
        ],
        constants.INCLUDE_GIT_ARG: [
            constants.DRY_RUN_ARG,
            constants.LIST_IMMUTABLE_ARG,
            constants.LIST_MUTABLE_ARG,
            constants.REPORT_ARG,
            constants.UNSET_ARG,
        ],
        constants.LIST_IMMUTABLE_ARG: [constants.INCLUDE_GIT_ARG],
        constants.LIST_MUTABLE_ARG: [constants.INCLUDE_GIT_ARG],
        constants.REPORT_ARG: [constants.INCLUDE_GIT_ARG, constants.UNSET_ARG],
        constants.UNSET_ARG: [
            constants.DRY_RUN_ARG,
            constants.INCLUDE_GIT_ARG,
        ],
    }

    # Make a list of the optional arguments supplied at the command line. The
    # arguments are represented in the Namespace object with underscores
    # raplacing hyphens, so convert between underscores and hyphens are
    # required.
    optional_args = compatibility.keys()
    optional_args_with_underscores = [
        oa[2:].replace("-", "_") for oa in optional_args
    ]
    supplied_optional_args_with_underscores = [
        oa for oa in optional_args_with_underscores if getattr(args, oa)
    ]
    supplied_optional_args = [
        "--{}".format(oa.replace("_", "-"))
        for oa in supplied_optional_args_with_underscores
    ]

    # Build a set of pairs of conflicting arguments.
    conflicting_arguments = set()
    for optional_arg in supplied_optional_args:
        other_supplied_args = [
            arg for arg in supplied_optional_args if arg != optional_arg
        ]
        compatible_args = compatibility.get(optional_arg)

        for arg in other_supplied_args:
            if arg not in compatible_args:
                argument_pair = tuple(sorted([optional_arg, arg]))
                conflicting_arguments.add(argument_pair)

    # Convert each argument pair into an error message.
    error_messages = ([
        "{} and {} cannot be passed together".format(*pair)
        for pair in conflicting_arguments
    ])

    return sorted(error_messages)


def _get_absolute_path(path):
    """Convert a path into an absolute path.

    Parameters
    ----------
    path : str
        A relative or absolute path.

    Returns
    -------
    str
        The absolute path.

    """
    if os.path.isabs(path):
        absolute_path = path
    else:
        current_working_directory = os.getcwd()
        absolute_path = os.path.join(current_working_directory, path)

    # Normalise the path to remove up-level references like "." and "..".
    absolute_path = os.path.normpath(absolute_path)

    return absolute_path


def _get_path_type(path):
    """Determine if a path is a directory, file or link.

    Parameters
    ----------
    path : str
        An absolute path.

    Returns
    -------
    str
        The type of object.

    Raises
    ------
    ObjectTypeError
        If the path is not an absolute path.
    PathDoesNotExistError
        If the path does not exist.

    """
    # Raise an exception if the path is not an absolute path.
    if not os.path.isabs(path):
        msg = "'{}' is not an absolute path".format(path)
        raise exceptions.ObjectTypeError(msg)

    # Raise an exception if the path does not exist.
    if not os.path.exists(path):
        msg = "The path '{}' does not exist".format(path)
        raise exceptions.PathDoesNotExistError(msg)

    if os.path.islink(path):
        path_type = constants.LINK
    elif os.path.isfile(path):
        path_type = constants.FILE
    elif os.path.isdir(path):
        path_type = constants.DIRECTORY

    return path_type


def _parse_args(argv):
    """Parse the command line input.

    Parameters
    ----------
    argv : list of str
        List of arguments from the command line, including the executable.

    Returns
    -------
    instance of Namespace
        Parsed arguments from the command line.

    """
    parser = argparse.ArgumentParser(
        description="Manage file immutability.",
        usage="%(prog)s [options] path",
    )

    parser.add_argument("path", help="the path to operate on")
    parser.add_argument(
        constants.DRY_RUN_SHORT_ARG,
        constants.DRY_RUN_ARG,
        action="store_true",
        help="make no changes",
    )
    parser.add_argument(
        constants.INCLUDE_GIT_SHORT_ARG,
        constants.INCLUDE_GIT_ARG,
        action="store_true",
        help="include .git directories (excluded by default)",
    )
    parser.add_argument(
        constants.LIST_IMMUTABLE_ARG,
        action="store_true",
        help="list all immutable files",
    )
    parser.add_argument(
        constants.LIST_MUTABLE_ARG,
        action="store_true",
        help="list all mutable files",
    )
    parser.add_argument(
        constants.REPORT_SHORT_ARG,
        constants.REPORT_ARG,
        action="store_true",
        help="display a status report",
    )
    parser.add_argument(
        constants.UNSET_SHORT_ARG,
        constants.UNSET_ARG,
        action="store_true",
        help="unset immutability",
    )
    parser.add_argument(
        constants.VERSION_SHORT_ARG,
        constants.VERSION_ARG,
        action="version",
        version="{} {}".format(entomb.__title__, entomb.__version__),
    )

    return parser.parse_args(argv[1:])


def _print_argument_conflict_errors(conflicts):
    """Print the list of command line argument conflicts.

    Parameters
    ----------
    conflicts : list of str
        A list of argument conflict messages.

    Returns
    -------
    None

    """
    print()
    for conflict in conflicts:
        print("ERROR:", conflict)


def _print_path_not_found_error(relative_path, absolute_path):
    """Print the details of a path which can't be found.

    Parameters
    ----------
    relative_path : str
        A relative path.
    absolute_path : str
        The absolute path which the relative path expanded to.

    Returns
    -------
    None

    """
    print()
    print("ERROR: The path you gave could not be found")
    print(">> You entered this path:", relative_path)

    # If the relative path expanded to a different absolute path, display the
    # absolute path.
    if relative_path != absolute_path:
        print(">> It was expanded to this:", absolute_path)


def _prompt_for_sudo():
    """Trigger the sudo prompt for a user without root privileges.

    Returns
    -------
    None

    """
    print()
    print("** To set or unset files' immutable attributes, root")
    print("** privileges are required.")
    print()
    subprocess.run(
        ["sudo", "-v"],
        check=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.DEVNULL,
    )
    print()


def _signal_handler(signum, frame):  # pylint: disable=unused-argument
    """Print an interrupt or termination message, then exit.

    Parameters
    ----------
    signum : int
        The signal number. Either 2 (SIGINT) or 15 (SIGTERM).
    frame : frame object
        Unused.

    Returns
    -------
    None

    """
    print()
    print()
    if signum == signal.SIGINT:
        print(">> Keyboard interrupt signal received. Exiting.")
    elif signum == signal.SIGTERM:
        print(">> Termination signal received. Exiting.")
    print()
    sys.exit(1)


def _user_has_root_privileges():
    """Determine whether the user currently has root privileges.

    Returns
    -------
    bool
        Whether the user currently has root privileges.

    """
    try:
        subprocess.run(
            ["sudo", "-ln"],
            check=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.DEVNULL,
        )
        has_root_privileges = True
    except subprocess.CalledProcessError:
        has_root_privileges = False

    return has_root_privileges
