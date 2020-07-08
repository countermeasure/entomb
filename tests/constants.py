import os


# Main directory paths.
DIRECTORY_PATH = "/tmp/entomb_testing"
IMMUTABLE_FILE_PATH = os.path.join(DIRECTORY_PATH, "immutable.txt")
LINK_PATH = os.path.join(DIRECTORY_PATH, "link.txt")
MUTABLE_FILE_PATH = os.path.join(DIRECTORY_PATH, "mutable.txt")
NAMED_PIPE_PATH = os.path.join(DIRECTORY_PATH, "fifo")
READABLE_BY_ROOT_FILE_PATH = os.path.join(
    DIRECTORY_PATH,
    "readable_by_root.txt",
)


# Subdirectory paths.
EMPTY_SUBDIRECTORY_PATH = os.path.join(DIRECTORY_PATH, "empty_directory")
SUBDIRECTORY_PATH = os.path.join(DIRECTORY_PATH, "subdirectory")
SUBDIRECTORY_IMMUTABLE_FILE_PATH = os.path.join(
    SUBDIRECTORY_PATH,
    "immutable.txt",
)
SUBDIRECTORY_LINK_PATH = os.path.join(SUBDIRECTORY_PATH, "link.txt")
SUBDIRECTORY_MUTABLE_FILE_PATH = os.path.join(SUBDIRECTORY_PATH, "mutable.txt")


# Fake git repo paths.
GIT_DIRECTORY_PATH = os.path.join(DIRECTORY_PATH, ".git")
GIT_DIRECTORY_MUTABLE_FILE_PATH = os.path.join(
    GIT_DIRECTORY_PATH,
    "mutable.txt",
)
GIT_SUBDIRECTORY_PATH = os.path.join(GIT_DIRECTORY_PATH, "subdirectory")
GIT_SUBDIRECTORY_MUTABLE_FILE_PATH = os.path.join(
    GIT_SUBDIRECTORY_PATH,
    "mutable.txt",
)


# Non-existent paths.
NON_EXISTENT_PATH = "/a/path/that/does/not/exist"
NON_PATH_STRING = "a non-path string"
RELATIVE_PATH = "relative/path"
