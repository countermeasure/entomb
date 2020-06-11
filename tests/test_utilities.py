import datetime
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

    def test_clear_line(self):
        """Test the clear_line function.

        """
        with mock.patch("builtins.print") as mocked_print:
            utilities.clear_line()
        expected = [mock.call("\033[K", end="")]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test_count_file_paths(self):
        """Test the count_file_paths function.

        """
        # Test a directory excluding git files with a print frequency of 1.
        with mock.patch("builtins.print") as mocked_print:
            actual_count = utilities.count_file_paths(
                constants.DIRECTORY_PATH,
                include_git=False,
                print_frequency=1,
            )
            expected_count = 6
            self.assertEqual(actual_count, expected_count)

        expected_output = [
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("Counting file paths: 1", end="\r"),
            mock.call("Counting file paths: 2", end="\r"),
            mock.call("Counting file paths: 3", end="\r"),
            mock.call("Counting file paths: 4", end="\r"),
            mock.call("Counting file paths: 5", end="\r"),
            mock.call("Counting file paths: 6", end="\r"),
            mock.call("\033[K", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected_output)

        # Test a directory including git files with a print frequency of 2.
        with mock.patch("builtins.print") as mocked_print:
            actual_count = utilities.count_file_paths(
                constants.DIRECTORY_PATH,
                include_git=True,
                print_frequency=2,
            )
            expected_count = 8
            self.assertEqual(actual_count, expected_count)

        expected_output = [
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("Counting file paths: 2", end="\r"),
            mock.call("Counting file paths: 4", end="\r"),
            mock.call("Counting file paths: 6", end="\r"),
            mock.call("Counting file paths: 8", end="\r"),
            mock.call("\033[K", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected_output)

        # Test an empty directory.
        with mock.patch("builtins.print") as mocked_print:
            actual_count = utilities.count_file_paths(
                constants.EMPTY_SUBDIRECTORY_PATH,
                include_git=False,
                print_frequency=1,
            )
            expected_count = 0
            self.assertEqual(actual_count, expected_count)

        expected_output = [
            mock.call("Counting file paths: 0", end="\r"),
            mock.call("\033[K", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected_output)

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

    def test_hide_cursor(self):
        """Test the hide_cursor function.

        """
        with mock.patch("builtins.print") as mocked_print:
            # The function is used as a decorator, but is easier to test as a
            # context manager.
            with utilities.hide_cursor():
                print("testing")
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("testing"),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

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

    def test_print_progress_bar(self):
        """Test the progress_bar function.

        """
        start_time = datetime.datetime.now()

        # Test progress of exactly 0%.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(microseconds=10)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=0,
                    total=10000,
                    print_frequency=100,
                )
        expected_progress_bar = (
            "░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0.0%"
        )
        expected = [
            mock.call("\033[K", end=""),
            mock.call(expected_progress_bar, end="\r"),
            ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test progress of exactly 50%.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(seconds=5)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=5000,
                    total=10000,
                    print_frequency=100,
                )
        expected_progress_bar = (
            "████████████████████░░░░░░░░░░░░░░░░░░░░  50.0%  |  5s to go"
        )
        expected = [
            mock.call("\033[K", end=""),
            mock.call(expected_progress_bar, end="\r"),
            ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test progress of exactly 100%.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(seconds=10)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=12345,
                    total=12345,
                    print_frequency=100,
                )
        expected_progress_bar = "████████████████████████████████████████"
        expected = [
            mock.call("\033[K", end=""),
            mock.call(expected_progress_bar, end="\r"),
            ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test progress rounding down to 99.9% rather than up to 100%.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(seconds=10)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=9999,
                    total=10000,
                    print_frequency=1,
                )
        expected_progress_bar = (
            "███████████████████████████████████████░  99.9%  |  0s to go"
        )
        expected = [
            mock.call("\033[K", end=""),
            mock.call(expected_progress_bar, end="\r"),
            ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test printing nothing when frequency condition is not met.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(seconds=1)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=1001,
                    total=10000,
                    print_frequency=100,
                )
        expected = []
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test for count of 0 and total of 0.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(milliseconds=10)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=0,
                    total=0,
                    print_frequency=1,
                )
        expected_progress_bar = "████████████████████████████████████████"
        expected = [
            mock.call("\033[K", end=""),
            mock.call(expected_progress_bar, end="\r"),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test for an operation which takes several hours.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("datetime.datetime") as mocked_datetime:
                now = start_time + datetime.timedelta(hours=1, minutes=23)
                mocked_datetime.now.return_value = now
                utilities.print_progress_bar(
                    start_time=start_time,
                    count=5840300,
                    total=21735498,
                    print_frequency=100,
                )
        expected_progress_bar = (
            "██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  "
            "26.8%  |  3h 45m 54s to go"
        )
        expected = [
            mock.call("\033[K", end=""),
            mock.call(expected_progress_bar, end="\r"),
            ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__add_percentage_to_progress_bar(self):
        """Test the _add_percentage_to_progress_bar function.

        """
        # Because _add_percentage_to_progress_bar() contributes to
        # print_progress_bar() it is not tested in isolation, but is tested as
        # part of print_progress_bar() by test_print_progress_bar().

    def test__add_time_to_progress_bar(self):
        """Test the _add_time_to_progress_bar function.

        """
        # Because _add_time_to_progress_bar() contributes to
        # print_progress_bar() it is not tested in isolation, but is tested as
        # part of print_progress_bar() by test_print_progress_bar().

    def test__build_progress_bar(self):
        """Test the _build_progress_bar function.

        """
        # Because _build_progress_bar() contributes to print_progress_bar() it
        # is not tested in isolation, but is tested as part of
        # print_progress_bar() by test_print_progress_bar().

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

    def test__readable_duration(self):
        """Test the _readable_duration function.

        """
        self.assertEqual(utilities._readable_duration(0), "0s")
        self.assertEqual(utilities._readable_duration(5), "5s")
        self.assertEqual(utilities._readable_duration(59.1), "59s")
        self.assertEqual(utilities._readable_duration(59.9), "1m 00s")
        self.assertEqual(utilities._readable_duration(305), "5m 05s")
        self.assertEqual(utilities._readable_duration(600.1), "10m 00s")
        self.assertEqual(utilities._readable_duration(3600), "1h 00m 00s")
        self.assertEqual(
            utilities._readable_duration(3600000),
            "1,000h 00m 00s",
        )

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
