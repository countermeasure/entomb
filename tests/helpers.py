import os
import shutil
import subprocess

from tests import constants


def file_is_immutable(path):
    """Whether a file has the immutable attribute set.

    Parameters
    ----------
    path : str
        An absolute path to a file.

    Returns
    -------
    bool
        True if the file's immmutable attribute is set, False if it is not.

    Raises
    ------
    CalledProcessError
        If the exit status of the chattr command is non-zero.

    """
    # Run the lsattr command.
    lsattr_result = subprocess.run(
        ["lsattr", path],
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )

    # Extract the immutable attribute from the command output.
    attributes = lsattr_result.stdout.split()[0]
    immutable_flag = list(attributes)[4]

    return immutable_flag == "i"


def set_file_immutable_attribute(path, immutable):
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
    CalledProcessError
        If the exit status of the chattr command is non-zero.

    """
    operation = "+i" if immutable else "-i"

    subprocess.run(["sudo", "chattr", operation, path], check=True)


def set_up():
    """Create temporary directories and files.

    Returns
    -------
    None

    """
    # Ensure that tests start with a clean slate.
    tear_down()

    # Create testing directories.
    os.makedirs(constants.EMPTY_SUBDIRECTORY_PATH)
    os.makedirs(constants.GIT_SUBDIRECTORY_PATH)
    os.makedirs(constants.SUBDIRECTORY_PATH)

    # Create testing files.
    open(constants.GIT_DIRECTORY_MUTABLE_FILE_PATH, "x").close()
    open(constants.GIT_SUBDIRECTORY_MUTABLE_FILE_PATH, "x").close()
    open(constants.IMMUTABLE_FILE_PATH, "x").close()
    open(constants.MUTABLE_FILE_PATH, "x").close()
    open(constants.SUBDIRECTORY_IMMUTABLE_FILE_PATH, "x").close()
    open(constants.SUBDIRECTORY_MUTABLE_FILE_PATH, "x").close()

    # Create testing links.
    os.symlink(constants.MUTABLE_FILE_PATH, constants.LINK_PATH)
    os.symlink(
        constants.SUBDIRECTORY_MUTABLE_FILE_PATH,
        constants.SUBDIRECTORY_LINK_PATH,
    )

    # Set immutability for some testing files.
    set_file_immutable_attribute(constants.IMMUTABLE_FILE_PATH, immutable=True)
    set_file_immutable_attribute(
        constants.SUBDIRECTORY_IMMUTABLE_FILE_PATH,
        immutable=True,
    )


def tear_down():
    """Delete temporary directories and files.

    Returns
    -------
    None

    """
    # Ensure all testing files are mutable, or they won't able to be deleted.
    for root_dir, _, filenames in os.walk(constants.DIRECTORY_PATH):
        for filename in filenames:
            file_path = os.path.join(root_dir, filename)
            if not os.path.islink(file_path):
                set_file_immutable_attribute(file_path, immutable=False)

    # Remove the testing directory.
    try:
        shutil.rmtree(constants.DIRECTORY_PATH)
    except FileNotFoundError:
        pass
