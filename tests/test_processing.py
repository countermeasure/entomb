import contextlib
import os
import subprocess
import unittest
import unittest.mock as mock

import entomb.exceptions as exceptions
import entomb.processing as processing
from tests import (
    constants,
    helpers,
)


class TestProcessing(unittest.TestCase):
    """Tests for the processing module.

    """

    def setUp(self):
        """Create temporary directories and files.

        """
        helpers.set_up()

    def test_process_objects(self):
        """Test the process_objects function.

        """
        # Test making files immutable excluding git files
        with mock.patch("builtins.print") as mocked_print:
            processing.process_objects(
                constants.DIRECTORY_PATH,
                immutable=True,
                include_git=False,
                dry_run=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Entomb objects"),
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
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Entombed 2 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call(
                "All 4 files for which immutability can be set are now "
                "entombed",
            ),
            mock.call("All 2 links were ignored"),
            mock.call(),
            mock.call("Errors"),
            mock.call("------"),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/fifo",
            ),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/readable_by_root.txt",
            ),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Confirm that all files for which the immutable attribute is settable
        # were made immutable.
        for root_dir, _, filenames in os.walk(constants.DIRECTORY_PATH):
            file_should_be_immutable = ".git" not in root_dir
            for filename in filenames:
                file_path = os.path.join(root_dir, filename)
                with contextlib.suppress(subprocess.CalledProcessError):
                    self.assertEqual(
                        helpers.file_is_immutable(file_path),
                        file_should_be_immutable,
                    )

        # Test making files mutable including git.
        with mock.patch("builtins.print") as mocked_print:
            processing.process_objects(
                constants.DIRECTORY_PATH,
                immutable=False,
                include_git=True,
                dry_run=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Unset objects"),
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
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Unset 4 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call(
                "All 6 files for which immutability can be set are now unset",
            ),
            mock.call("All 2 links were ignored"),
            mock.call(),
            mock.call("Errors"),
            mock.call("------"),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/fifo",
            ),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/readable_by_root.txt",
            ),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Confirm that all files for which the immutable attribute is settable
        # were made mutable.
        for root_dir, _, filenames in os.walk(constants.DIRECTORY_PATH):
            for filename in filenames:
                file_path = os.path.join(root_dir, filename)
                with contextlib.suppress(subprocess.CalledProcessError):
                    self.assertFalse(helpers.file_is_immutable(file_path))

        # Test a dry-run for making files immutable excluding git.
        with mock.patch("builtins.print") as mocked_print:
            processing.process_objects(
                constants.DIRECTORY_PATH,
                immutable=True,
                include_git=False,
                dry_run=True,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Entomb objects"),
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
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Entombed 4 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call(
                "All 4 files for which immutability can be set are now "
                "entombed",
            ),
            mock.call("All 2 links were ignored"),
            mock.call(),
            mock.call("Errors"),
            mock.call("------"),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/fifo",
            ),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/readable_by_root.txt",
            ),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Confirm that no files were made immutable.
        for root_dir, _, filenames in os.walk(constants.DIRECTORY_PATH):
            for filename in filenames:
                file_path = os.path.join(root_dir, filename)
                with contextlib.suppress(subprocess.CalledProcessError):
                    self.assertFalse(helpers.file_is_immutable(file_path))

        # Test processing an empty directory.
        with mock.patch("builtins.print") as mocked_print:
            processing.process_objects(
                constants.EMPTY_SUBDIRECTORY_PATH,
                immutable=True,
                include_git=False,
                dry_run=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Entomb objects"),
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
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("No files were found"),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test processing a non-existent path.
        with self.assertRaises(AssertionError):
            processing.process_objects(
                constants.NON_EXISTENT_PATH,
                immutable=True,
                include_git=True,
                dry_run=False,
            )

        # Test a named pipe.
        with mock.patch("builtins.print") as mocked_print:
            processing.process_objects(
                constants.NAMED_PIPE_PATH,
                immutable=False,
                include_git=True,
                dry_run=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Unset objects"),
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
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Unset 0 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call(
                "All 0 files for which immutability can be set are now unset",
            ),
            mock.call("All 0 links were ignored"),
            mock.call(),
            mock.call("Errors"),
            mock.call("------"),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/fifo",
            ),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a file which is readable only by root.
        with mock.patch("builtins.print") as mocked_print:
            processing.process_objects(
                constants.READABLE_BY_ROOT_FILE_PATH,
                immutable=True,
                include_git=False,
                dry_run=False,
            )
        expected = [
            mock.call("\033[?25l", end=""),
            mock.call("Entomb objects"),
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
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Entombed 0 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call(
                "All 0 files for which immutability can be set are now "
                "entombed",
            ),
            mock.call("All 0 links were ignored"),
            mock.call(),
            mock.call("Errors"),
            mock.call("------"),
            mock.call(
                ">> Immutable attribute not settable for "
                "/tmp/entomb_testing/readable_by_root.txt",
            ),
            mock.call(),
            mock.call("\033[?25h", end=""),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__print_errors(self):
        """Test the _print_errors function.

        """
        # Test with no errors.
        with mock.patch("builtins.print") as mocked_print:
            processing._print_errors([])
        expected = []
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test with three errors.
        with mock.patch("builtins.print") as mocked_print:
            processing._print_errors([
                "ERROR: Message 1",
                "ERROR: Message 2",
                "ERROR: Message 3",
            ])
        expected = [
            mock.call("Errors"),
            mock.call("------"),
            mock.call(">> ERROR: Message 1"),
            mock.call(">> ERROR: Message 2"),
            mock.call(">> ERROR: Message 3"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test with 12 errors.
        with mock.patch("builtins.print") as mocked_print:
            processing._print_errors([
                "ERROR: Message 1",
                "ERROR: Message 2",
                "ERROR: Message 3",
                "ERROR: Message 4",
                "ERROR: Message 5",
                "ERROR: Message 6",
                "ERROR: Message 7",
                "ERROR: Message 8",
                "ERROR: Message 9",
                "ERROR: Message 10",
                "ERROR: Message 11",
                "ERROR: Message 12",
            ])
        expected = [
            mock.call("Errors"),
            mock.call("------"),
            mock.call(">> ERROR: Message 1"),
            mock.call(">> ERROR: Message 2"),
            mock.call(">> ERROR: Message 3"),
            mock.call(">> ERROR: Message 4"),
            mock.call(">> ERROR: Message 5"),
            mock.call(">> ERROR: Message 6"),
            mock.call(">> ERROR: Message 7"),
            mock.call(">> ERROR: Message 8"),
            mock.call(">> ERROR: Message 9"),
            mock.call(">> ERROR: Message 10"),
            mock.call(">> Plus 2 more errors"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__process_object(self):
        """Test the _process_object function.

        """
        # Test making a mutable file immutable, then return it to its original
        # state.
        processing._process_object(
            constants.MUTABLE_FILE_PATH,
            immutable=True,
            dry_run=False,
        )
        self.assertTrue(helpers.file_is_immutable(constants.MUTABLE_FILE_PATH))
        processing._process_object(
            constants.MUTABLE_FILE_PATH,
            immutable=False,
            dry_run=False,
        )

        # Test making a mutable file mutable.
        processing._process_object(
            constants.MUTABLE_FILE_PATH,
            immutable=False,
            dry_run=False,
        )
        self.assertFalse(
            helpers.file_is_immutable(constants.MUTABLE_FILE_PATH),
        )

        # Test making an immutable file mutable, then return it to its original
        # state.
        processing._process_object(
            constants.IMMUTABLE_FILE_PATH,
            immutable=False,
            dry_run=False,
        )
        self.assertFalse(
            helpers.file_is_immutable(constants.IMMUTABLE_FILE_PATH),
        )
        processing._process_object(
            constants.IMMUTABLE_FILE_PATH,
            immutable=True,
            dry_run=False,
        )

        # Test making an immutable file immutable.
        processing._process_object(
            constants.IMMUTABLE_FILE_PATH,
            immutable=True,
            dry_run=False,
        )
        self.assertTrue(
            helpers.file_is_immutable(constants.IMMUTABLE_FILE_PATH),
        )

        # Test making an immutable file mutable as a dry run.
        processing._process_object(
            constants.IMMUTABLE_FILE_PATH,
            immutable=False,
            dry_run=True,
        )
        self.assertTrue(
            helpers.file_is_immutable(constants.IMMUTABLE_FILE_PATH),
        )

        # Test making a link immutable.
        with self.assertRaises(AssertionError):
            processing._process_object(
                constants.LINK_PATH,
                immutable=True,
                dry_run=False,
            )

        # Test making a directory mutable.
        with self.assertRaises(AssertionError):
            processing._process_object(
                constants.DIRECTORY_PATH,
                immutable=False,
                dry_run=False,
            )

        # Test making a non-existent path mutable.
        with self.assertRaises(AssertionError):
            processing._process_object(
                constants.NON_EXISTENT_PATH,
                immutable=False,
                dry_run=False,
            )

    def test__set_attribute(self):
        """Test the _set_attribute function.

        """
        # Test making an immutable file mutable.
        processing._set_attribute("-i", constants.IMMUTABLE_FILE_PATH)
        self.assertFalse(
            helpers.file_is_immutable(constants.IMMUTABLE_FILE_PATH),
        )

        # Test making a mutable file immutable.
        processing._set_attribute("+i", constants.IMMUTABLE_FILE_PATH)
        self.assertTrue(
            helpers.file_is_immutable(constants.IMMUTABLE_FILE_PATH),
        )

        # Test making a non-existent path to immutable.
        with self.assertRaises(exceptions.SetAttributeError):
            processing._set_attribute("+i", constants.NON_EXISTENT_PATH)

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
