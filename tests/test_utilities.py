import unittest
import unittest.mock as mock

import entomb.exceptions as exceptions
import entomb.utilities as utilities
from tests import (
    constants,
    helpers,
)


class TestUtilities(unittest.TestCase):
    """Tests for the utilities module.

    """

    def setUp(self):
        """Create temporary directories and files.

        """
        helpers.set_up()

    def test_file_is_immutable(self):
        """Test the file_is_immutable function.

        """
        # Test an immutable file path.
        self.assertTrue(
            utilities.file_is_immutable(constants.IMMUTABLE_FILE_PATH),
        )

        # Test a mutable file path.
        self.assertFalse(
            utilities.file_is_immutable(constants.MUTABLE_FILE_PATH),
        )

        # Test a directory path.
        with self.assertRaises(exceptions.ObjectTypeError):
            utilities.file_is_immutable(constants.DIRECTORY_PATH)

        # Test a link path.
        with self.assertRaises(exceptions.ObjectTypeError):
            utilities.file_is_immutable(constants.LINK_PATH)

        # Test a path which does not exist.
        with self.assertRaises(exceptions.PathDoesNotExistError):
            utilities.file_is_immutable(constants.NON_EXISTENT_PATH)

        # Test a string which can't be parsed as a path.
        with self.assertRaises(exceptions.PathDoesNotExistError):
            utilities.file_is_immutable(constants.NON_PATH_STRING)

    def test_file_paths(self):
        """Test the file_paths function.

        """
        # Test a directory excluding git files.
        actual = utilities.file_paths(
            constants.DIRECTORY_PATH,
            include_git=False,
        )
        expected = [
            constants.IMMUTABLE_FILE_PATH,
            constants.LINK_PATH,
            constants.MUTABLE_FILE_PATH,
            constants.SUBDIRECTORY_IMMUTABLE_FILE_PATH,
            constants.SUBDIRECTORY_LINK_PATH,
            constants.SUBDIRECTORY_MUTABLE_FILE_PATH,
        ]
        self.assertEqual(sorted(actual), sorted(expected))

        # Test a directory including git files.
        actual = utilities.file_paths(
            constants.DIRECTORY_PATH,
            include_git=True,
        )
        expected = [
            constants.GIT_DIRECTORY_MUTABLE_FILE_PATH,
            constants.GIT_SUBDIRECTORY_MUTABLE_FILE_PATH,
            constants.IMMUTABLE_FILE_PATH,
            constants.LINK_PATH,
            constants.MUTABLE_FILE_PATH,
            constants.SUBDIRECTORY_IMMUTABLE_FILE_PATH,
            constants.SUBDIRECTORY_LINK_PATH,
            constants.SUBDIRECTORY_MUTABLE_FILE_PATH,
        ]
        self.assertEqual(sorted(actual), sorted(expected))

        # Test a file.
        actual = utilities.file_paths(
            constants.IMMUTABLE_FILE_PATH,
            include_git=False,
        )
        expected = [constants.IMMUTABLE_FILE_PATH]
        self.assertEqual(sorted(actual), sorted(expected))

        # Test a link.
        actual = utilities.file_paths(constants.LINK_PATH, include_git=False)
        expected = [constants.LINK_PATH]
        self.assertEqual(sorted(actual), sorted(expected))

        # Test a directory which does not exist.
        with self.assertRaises(exceptions.PathDoesNotExistError):
            paths = utilities.file_paths(
                constants.NON_PATH_STRING,
                include_git=True,
            )
            # Ths exception will only be raised once the generator is iterated.
            next(paths)

    def test_print_header(self):
        """Test the print_header function.

        """
        with mock.patch("builtins.print") as mocked_print:
            utilities.print_header("Header")
        expected = [
            mock.call("Header"),
            mock.call("------"),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__get_immutable_flag(self):
        """Test the _get_immutable_flag function.

        """
        # Test an immutable file.
        actual = utilities._get_immutable_flag(constants.IMMUTABLE_FILE_PATH)
        expected = "i"
        self.assertEqual(actual, expected)

        # Test a mutable file.
        actual = utilities._get_immutable_flag(constants.MUTABLE_FILE_PATH)
        expected = "-"
        self.assertEqual(actual, expected)

        # Test a link.
        with self.assertRaises(exceptions.ProcessingError):
            actual = utilities._get_immutable_flag(constants.LINK_PATH)

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
