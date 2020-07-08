import unittest
import unittest.mock as mock

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
            mock.call("\033[?25l", end=""),
            mock.call("List immutable files"),
            mock.call(),
            mock.call("Immutable files"),
            mock.call("---------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/immutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  12.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  25.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "███████████████░░░░░░░░░░░░░░░░░░░░░░░░░  37.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████░░░░░░░░░░░░░░░░░░░░  50.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "█████████████████████████░░░░░░░░░░░░░░░  62.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/subdirectory/immutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "██████████████████████████████░░░░░░░░░░  75.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "███████████████████████████████████░░░░░  87.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("6 files were examined"),
            mock.call("2 files are immutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
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
            mock.call("\033[?25l", end=""),
            mock.call("List immutable files"),
            mock.call(),
            mock.call("Immutable files"),
            mock.call("---------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/immutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  30.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████░░░░░░░░░░░░░░░░░░░░░░░░  40.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████░░░░░░░░░░░░░░░░░░░░  50.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████░░░░░░░░░░░░░░░░  60.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████░░░░░░░░░░░░  70.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/subdirectory/immutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████░░░░░░░░  80.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████░░░░  90.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("8 files were examined"),
            mock.call("2 files are immutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
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
            mock.call("\033[?25l", end=""),
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  12.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  25.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/mutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "███████████████░░░░░░░░░░░░░░░░░░░░░░░░░  37.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████░░░░░░░░░░░░░░░░░░░░  50.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "█████████████████████████░░░░░░░░░░░░░░░  62.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "██████████████████████████████░░░░░░░░░░  75.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "███████████████████████████████████░░░░░  87.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/subdirectory/mutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("6 files were examined"),
            mock.call("2 files are mutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
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
            mock.call("\033[?25l", end=""),
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/mutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  30.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████░░░░░░░░░░░░░░░░░░░░░░░░  40.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████░░░░░░░░░░░░░░░░░░░░  50.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/.git/mutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████░░░░░░░░░░░░░░░░  60.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/.git/subdirectory/mutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████░░░░░░░░░░░░  70.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████░░░░░░░░  80.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████░░░░  90.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("/tmp/entomb_testing/subdirectory/mutable.txt"),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("8 files were examined"),
            mock.call("4 files are mutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
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
            mock.call("\033[?25l", end=""),
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "█████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  12.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  25.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "███████████████░░░░░░░░░░░░░░░░░░░░░░░░░  37.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████░░░░░░░░░░░░░░░░░░░░  50.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "█████████████████████████░░░░░░░░░░░░░░░  62.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "██████████████████████████████░░░░░░░░░░  75.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "███████████████████████████████████░░░░░  87.5%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("-"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("6 files were examined"),
            mock.call("0 files are mutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test for a non-existent path.
        with self.assertRaises(AssertionError):
            listing.list_files(
                constants.NON_EXISTENT_PATH,
                immutable=False,
                include_git=False,
            )

        # Test a named pipe.
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.NAMED_PIPE_PATH,
                immutable=False,
                include_git=True,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("List mutable files"),
            mock.call(),
            mock.call("Mutable files"),
            mock.call("-------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("-"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("1 files were examined"),
            mock.call("0 files are mutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a file which is readable only by root.
        with mock.patch("builtins.print") as mocked_print:
            listing.list_files(
                constants.READABLE_BY_ROOT_FILE_PATH,
                immutable=True,
                include_git=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("List immutable files"),
            mock.call(),
            mock.call("Immutable files"),
            mock.call("---------------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call("\033[K", end=""),
            mock.call("-"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("1 files were examined"),
            mock.call("0 files are immutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

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
        with self.assertRaises(AssertionError):
            listing._print_the_path(
                constants.NON_EXISTENT_PATH,
                immutable=True,
            )
        with self.assertRaises(AssertionError):
            listing._print_the_path(constants.DIRECTORY_PATH, immutable=False)
        with self.assertRaises(AssertionError):
            listing._print_the_path(constants.LINK_PATH, immutable=True)

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
