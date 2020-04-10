import unittest
import unittest.mock as mock

import entomb.exceptions as exceptions
import entomb.listing as listing
from tests import (
    constants,
    helpers,
)


class TestListing(unittest.TestCase):
    """Tests for the listing module.

    """

    def setUp(self):
        """Create temporary directories and files.

        """
        helpers.set_up()

    def test_list_files(self):
        """Test the list_files function.

        """
        # Test immutable files excluding git.
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.DIRECTORY_PATH,
                immutable=True,
                include_git=False,
            )
        expected = [
            mock.call("List immutable files"),
            mock.call(),
            mock.call("Immutable files"),
            mock.call("---------------"),
            mock.call("/tmp/entomb_testing/immutable.txt"),
            mock.call("Examined 1 files and 0 links", end="\r"),
            mock.call("Examined 1 files and 1 links", end="\r"),
            mock.call("Examined 2 files and 1 links", end="\r"),
            mock.call("/tmp/entomb_testing/subdirectory/immutable.txt"),
            mock.call("Examined 3 files and 1 links", end="\r"),
            mock.call("Examined 3 files and 2 links", end="\r"),
            mock.call("Examined 4 files and 2 links", end="\r"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("4 files were examined"),
            mock.call("2 files are immutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test immutable files including git.
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.DIRECTORY_PATH,
                immutable=True,
                include_git=True,
            )
        expected = [
            mock.call("List immutable files"),
            mock.call(),
            mock.call("Immutable files"),
            mock.call("---------------"),
            mock.call("/tmp/entomb_testing/immutable.txt"),
            mock.call("Examined 1 files and 0 links", end="\r"),
            mock.call("Examined 1 files and 1 links", end="\r"),
            mock.call("Examined 2 files and 1 links", end="\r"),
            mock.call("Examined 3 files and 1 links", end="\r"),
            mock.call("Examined 4 files and 1 links", end="\r"),
            mock.call("/tmp/entomb_testing/subdirectory/immutable.txt"),
            mock.call("Examined 5 files and 1 links", end="\r"),
            mock.call("Examined 5 files and 2 links", end="\r"),
            mock.call("Examined 6 files and 2 links", end="\r"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("6 files were examined"),
            mock.call("2 files are immutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test mutable files excluding git.
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.DIRECTORY_PATH,
                immutable=False,
                include_git=False,
            )
        expected = [
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Examined 1 files and 0 links", end="\r"),
            mock.call("Examined 1 files and 1 links", end="\r"),
            mock.call("/tmp/entomb_testing/mutable.txt"),
            mock.call("Examined 2 files and 1 links", end="\r"),
            mock.call("Examined 3 files and 1 links", end="\r"),
            mock.call("Examined 3 files and 2 links", end="\r"),
            mock.call("/tmp/entomb_testing/subdirectory/mutable.txt"),
            mock.call("Examined 4 files and 2 links", end="\r"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("4 files were examined"),
            mock.call("2 files are mutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test mutable files including git.
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.DIRECTORY_PATH,
                immutable=False,
                include_git=True,
            )
        expected = [
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Examined 1 files and 0 links", end="\r"),
            mock.call("Examined 1 files and 1 links", end="\r"),
            mock.call("/tmp/entomb_testing/mutable.txt"),
            mock.call("Examined 2 files and 1 links", end="\r"),
            mock.call("/tmp/entomb_testing/.git/mutable.txt"),
            mock.call("Examined 3 files and 1 links", end="\r"),
            mock.call("/tmp/entomb_testing/.git/subdirectory/mutable.txt"),
            mock.call("Examined 4 files and 1 links", end="\r"),
            mock.call("Examined 5 files and 1 links", end="\r"),
            mock.call("Examined 5 files and 2 links", end="\r"),
            mock.call("/tmp/entomb_testing/subdirectory/mutable.txt"),
            mock.call("Examined 6 files and 2 links", end="\r"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("6 files were examined"),
            mock.call("4 files are mutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test mutable files excluding git after making all files immutable.
        helpers.set_file_immutable_attribute(
            constants.GIT_SUBDIRECTORY_MUTABLE_FILE_PATH,
            immutable=True,
        )
        helpers.set_file_immutable_attribute(
            constants.MUTABLE_FILE_PATH,
            immutable=True,
        )
        helpers.set_file_immutable_attribute(
            constants.SUBDIRECTORY_MUTABLE_FILE_PATH,
            immutable=True,
        )
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.DIRECTORY_PATH,
                immutable=False,
                include_git=False,
            )
        expected = [
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Examined 1 files and 0 links", end="\r"),
            mock.call("Examined 1 files and 1 links", end="\r"),
            mock.call("Examined 2 files and 1 links", end="\r"),
            mock.call("Examined 3 files and 1 links", end="\r"),
            mock.call("Examined 3 files and 2 links", end="\r"),
            mock.call("Examined 4 files and 2 links", end="\r"),
            mock.call("-"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("4 files were examined"),
            mock.call("0 files are mutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__clear_line(self):
        """Test the _clear_line function.

        """
        with mock.patch("sys.stdout") as mocked_stdout:
            listing._clear_line()
        expected = [
            mock.call.write("\x1b[K"),
            mock.call.flush(),
        ]
        self.assertEqual(mocked_stdout.mock_calls, expected)

    def test__print_the_path(self):
        """Test the _print_the_path function.

        """
        self.assertTrue(
            listing._print_the_path(
                constants.IMMUTABLE_FILE_PATH,
                immutable=True,
            ),
        )
        self.assertFalse(
            listing._print_the_path(
                constants.IMMUTABLE_FILE_PATH,
                immutable=False,
            ),
        )
        self.assertFalse(
            listing._print_the_path(
                constants.MUTABLE_FILE_PATH,
                immutable=True,
            ),
        )
        self.assertTrue(
            listing._print_the_path(
                constants.MUTABLE_FILE_PATH,
                immutable=False,
            ),
        )
        with self.assertRaises(exceptions.ObjectTypeError):
            listing._print_the_path(constants.DIRECTORY_PATH, immutable=False)
        with self.assertRaises(exceptions.ObjectTypeError):
            listing._print_the_path(constants.LINK_PATH, immutable=True)

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
