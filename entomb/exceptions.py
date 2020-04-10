class ObjectTypeError(Exception):
    """Raise when the wrong type of object is given."""


class PathDoesNotExistError(Exception):
    """Raise when a path does not exist."""


class ProcessingError(Exception):
    """Raise when a subprocess call exits with a non-zero status."""
