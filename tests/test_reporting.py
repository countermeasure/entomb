import unittest
import unittest.mock as mock

import entomb.reporting as reporting
from tests import (
    constants,
    helpers,
)


class TestReporting(unittest.TestCase):
    """Tests for the reporting module.

    """

    def setUp(self):
        """Create temporary directories and files.

        """
        helpers.set_up()

    def test_print_report(self):
        """Test the print_report function.

        """
        # Test a link.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(constants.LINK_PATH, include_git=True)
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Report"),
            mock.call("------"),
            mock.call("A link has no immutable attribute"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test an immutable file.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.IMMUTABLE_FILE_PATH,
                include_git=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Report"),
            mock.call("------"),
            mock.call("File is immutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a mutable file.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.MUTABLE_FILE_PATH,
                include_git=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Report"),
            mock.call("------"),
            mock.call("File is mutable"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a named pipe.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.NAMED_PIPE_PATH,
                include_git=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Report"),
            mock.call("------"),
            mock.call("Immutable attribute could not be accessed"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a file which is readable only by root.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.READABLE_BY_ROOT_FILE_PATH,
                include_git=True,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Report"),
            mock.call("------"),
            mock.call("Immutable attribute could not be accessed"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a directory including git.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.DIRECTORY_PATH,
                include_git=True,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Progress"),
            mock.call("--------"),
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
            mock.call(),
            mock.call(),
            mock.call("Report"),
            mock.call("----------------------------------------"),
            mock.call("Immutable files", "                       2"),
            mock.call("----------------------------------------"),
            mock.call("Mutable files", "                         4"),
            mock.call("----------------------------------------"),
            mock.call("Inaccessible files", "                    2"),
            mock.call("----------------------------------------"),
            mock.call("All files", "                             8"),
            mock.call("----------------------------------------"),
            mock.call("Entombed", "                            25%"),
            mock.call("----------------------------------------"),
            mock.call("Links", "                                 2"),
            mock.call("----------------------------------------"),
            mock.call("Sub-directories", "                       4"),
            mock.call("----------------------------------------"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a directory excluding git.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.DIRECTORY_PATH,
                include_git=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Progress"),
            mock.call("--------"),
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
            mock.call(),
            mock.call(),
            mock.call("Report"),
            mock.call("----------------------------------------"),
            mock.call("Immutable files", "                       2"),
            mock.call("----------------------------------------"),
            mock.call("Mutable files", "                         2"),
            mock.call("----------------------------------------"),
            mock.call("Inaccessible files", "                    2"),
            mock.call("----------------------------------------"),
            mock.call("All files", "                             6"),
            mock.call("----------------------------------------"),
            mock.call("Entombed", "                            33%"),
            mock.call("----------------------------------------"),
            mock.call("Links", "                                 2"),
            mock.call("----------------------------------------"),
            mock.call("Sub-directories", "                       2"),
            mock.call("----------------------------------------"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test an empty directory.
        with mock.patch("builtins.print") as mocked_print:
            reporting.produce_report(
                constants.EMPTY_SUBDIRECTORY_PATH,
                include_git=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Progress"),
            mock.call("--------"),
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
            mock.call("\033[K", end=""),
            mock.call(
                "████████████████████████████████████████",
                end="\r",
            ),
            mock.call(),
            mock.call(),
            mock.call("Report"),
            mock.call("----------------------------------------"),
            mock.call("Immutable files", "                       0"),
            mock.call("----------------------------------------"),
            mock.call("Mutable files", "                         0"),
            mock.call("----------------------------------------"),
            mock.call("All files", "                             0"),
            mock.call("----------------------------------------"),
            mock.call("Entombed", "                            n/a"),
            mock.call("----------------------------------------"),
            mock.call("Links", "                                 0"),
            mock.call("----------------------------------------"),
            mock.call("Sub-directories", "                       0"),
            mock.call("----------------------------------------"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a non-existent path.
        with self.assertRaises(AssertionError):
            reporting.produce_report(
                constants.NON_EXISTENT_PATH,
                include_git=False,
            )

    def test__print_abbreviated_report(self):
        """Test the _print_abbreviated_report function.

        """
        # Test an immutable file.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_abbreviated_report(constants.IMMUTABLE_FILE_PATH)
        expected = [
            mock.call("Report"),
            mock.call("------"),
            mock.call("File is immutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a mutable file.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_abbreviated_report(constants.MUTABLE_FILE_PATH)
        expected = [
            mock.call("Report"),
            mock.call("------"),
            mock.call("File is mutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a link.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_abbreviated_report(constants.LINK_PATH)
        expected = [
            mock.call("Report"),
            mock.call("------"),
            mock.call("A link has no immutable attribute"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a directory.
        with self.assertRaises(AssertionError):
            reporting._print_abbreviated_report(constants.DIRECTORY_PATH)

        # Test a non-existent path.
        with self.assertRaises(AssertionError):
            reporting._print_abbreviated_report(constants.NON_EXISTENT_PATH)

        # Test a named pipe.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_abbreviated_report(constants.NAMED_PIPE_PATH)
        expected = [
            mock.call("Report"),
            mock.call("------"),
            mock.call("Immutable attribute could not be accessed"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a file which is readable only by root.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_abbreviated_report(
                constants.READABLE_BY_ROOT_FILE_PATH,
            )
        expected = [
            mock.call("Report"),
            mock.call("------"),
            mock.call("Immutable attribute could not be accessed"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__print_full_report(self):
        """Test the _print_full_report function.

        """
        # Test with a non-zero entombed percentage.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_full_report(
                directory_count=6,
                link_count=5,
                immutable_file_count=8,
                inaccessible_file_count=3,
                mutable_file_count=27,
            )
        expected = [
            mock.call("Report"),
            mock.call("----------------------------------------"),
            mock.call("Immutable files", "                       8"),
            mock.call("----------------------------------------"),
            mock.call("Mutable files", "                        27"),
            mock.call("----------------------------------------"),
            mock.call("Inaccessible files", "                    3"),
            mock.call("----------------------------------------"),
            mock.call("All files", "                            38"),
            mock.call("----------------------------------------"),
            mock.call("Entombed", "                            21%"),
            mock.call("----------------------------------------"),
            mock.call("Links", "                                 5"),
            mock.call("----------------------------------------"),
            mock.call("Sub-directories", "                       5"),
            mock.call("----------------------------------------"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test with an n/a entombed percentage.
        with mock.patch("builtins.print") as mocked_print:
            reporting._print_full_report(
                directory_count=3,
                link_count=0,
                immutable_file_count=0,
                inaccessible_file_count=0,
                mutable_file_count=0,
            )
        expected = [
            mock.call("Report"),
            mock.call("----------------------------------------"),
            mock.call("Immutable files", "                       0"),
            mock.call("----------------------------------------"),
            mock.call("Mutable files", "                         0"),
            mock.call("----------------------------------------"),
            mock.call("All files", "                             0"),
            mock.call("----------------------------------------"),
            mock.call("Entombed", "                            n/a"),
            mock.call("----------------------------------------"),
            mock.call("Links", "                                 0"),
            mock.call("----------------------------------------"),
            mock.call("Sub-directories", "                       2"),
            mock.call("----------------------------------------"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
