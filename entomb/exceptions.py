class FileIntegrityError(Exception):
    """Raise when there is a mismatch between a file and its data files."""


class GetAttributeError(Exception):
    """Raise when the immutable attribute cannot be accessed."""


class SetAttributeError(Exception):
    """Raise when the immutable attribute cannot be set."""
