# Command line arguments.
CHECK_ARG = "--check"
CHECK_SHORT_ARG = "-c"
DRY_RUN_ARG = "--dry-run"
DRY_RUN_SHORT_ARG = "-d"
INCLUDE_GIT_ARG = "--include-git"
INCLUDE_GIT_SHORT_ARG = "-g"
LIST_IMMUTABLE_ARG = "--list-immutable"
LIST_MUTABLE_ARG = "--list-mutable"
REPORT_ARG = "--report"
REPORT_SHORT_ARG = "-r"
UNSET_ARG = "--unset"
UNSET_SHORT_ARG = "-u"
VERSION_ARG = "--version"
VERSION_SHORT_ARG = "-v"


# Entomb directories.
ENTOMB_DIRECTORY_NAME = ".entomb"
HASHES_DIRECTORY_NAME = "hashes"
HASH_FILES_PER_FILE = 3
LOGS_DIRECTORY_NAME = "logs"


# File attributes.
IMMUTABLE_ATTRIBUTE = "+i"
MUTABLE_ATTRIBUTE = "-i"


# Formatting
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
TABLE_WIDTH = 40


# Logging actions.
# TODO: Is this needed? Change to "ADD" and "REMOVE" instead? More
# git-commit-like.
ADDED = "ADDED"
REMOVED = "REMOVED"


# Path types.
DIRECTORY = "directory"
FILE = "file"
LINK = "link"
