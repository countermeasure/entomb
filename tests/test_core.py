import argparse
import io
import os
import signal
import subprocess
import unittest
import unittest.mock as mock

import entomb.core as core
import entomb.exceptions as exceptions
from tests import (
    constants,
    helpers,
)


EXECUTABLE = "entomb"


class TestCore(unittest.TestCase):
    """Tests for the core module.

    """

    def setUp(self):
        """Create temporary directories and files.

        """
        helpers.set_up()

    def test_main(self):
        """Test the main function.

        """
        # Test invoking with conflicting arguments.
        with mock.patch("builtins.print") as mocked_print:
            core.main([
                EXECUTABLE,
                constants.DIRECTORY_PATH,
                "-d",
                "--list-immutable",
            ])
        expected = [
            mock.call(),
            mock.call(
                "ERROR:",
                "--dry-run and --list-immutable cannot be passed together",
            ),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test invoking with a non-existent path as the target.
        with mock.patch("builtins.print") as mocked_print:
            core.main([EXECUTABLE, constants.NON_EXISTENT_PATH])
        expected = [
            mock.call(),
            mock.call("ERROR: The path you gave could not be found"),
            mock.call(
                ">> You entered this path:",
                "/a/path/that/does/not/exist",
            ),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test generating a report for a directory including git files.
        with mock.patch("builtins.print") as mocked_print:
            core.main([EXECUTABLE, constants.DIRECTORY_PATH, "-r"])
        expected = [
            mock.call(),
            mock.call("======"),
            mock.call("Entomb"),
            mock.call("======"),
            mock.call(),
            mock.call("Directory"),
            mock.call("---------"),
            mock.call("/tmp/entomb_testing"),
            mock.call(),
            mock.call("Operation"),
            mock.call("---------"),
            mock.call("Produce report"),
            mock.call(),
            mock.call("Progress"),
            mock.call("--------"),
            mock.call("-", end="\r"),
            mock.call(
                "Examined 1 files and 0 links in 1 directories",
                end="\r",
            ),
            mock.call(
                "Examined 1 files and 1 links in 1 directories",
                end="\r",
            ),
            mock.call(
                "Examined 2 files and 1 links in 1 directories",
                end="\r",
            ),
            mock.call(
                "Examined 3 files and 1 links in 3 directories",
                end="\r",
            ),
            mock.call(
                "Examined 3 files and 2 links in 3 directories",
                end="\r",
            ),
            mock.call(
                "Examined 4 files and 2 links in 3 directories",
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
            mock.call("All files", "                             4"),
            mock.call("----------------------------------------"),
            mock.call("Entombed", "                            50%"),
            mock.call("----------------------------------------"),
            mock.call("Sub-directories", "                       2"),
            mock.call("----------------------------------------"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test printing a list of immutable files.
        with mock.patch("builtins.print") as mocked_print:
            core.main(
                [EXECUTABLE, constants.SUBDIRECTORY_PATH, "--list-immutable"],
            )
        expected = [
            mock.call(),
            mock.call("======"),
            mock.call("Entomb"),
            mock.call("======"),
            mock.call(),
            mock.call("Directory"),
            mock.call("---------"),
            mock.call("/tmp/entomb_testing/subdirectory"),
            mock.call(),
            mock.call("Operation"),
            mock.call("---------"),
            mock.call("List immutable files"),
            mock.call(),
            mock.call("Immutable files"),
            mock.call("---------------"),
            mock.call("/tmp/entomb_testing/subdirectory/immutable.txt"),
            mock.call("Examined 1 files and 0 links", end="\r"),
            mock.call("Examined 1 files and 1 links", end="\r"),
            mock.call("Examined 2 files and 1 links", end="\r"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("2 files were examined"),
            mock.call("1 files are immutable"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test printing a list of mutable files including git files.
        with mock.patch("builtins.print") as mocked_print:
            core.main(
                [EXECUTABLE, constants.DIRECTORY_PATH, "-g", "--list-mutable"],
            )
        expected = [
            mock.call(),
            mock.call("======"),
            mock.call("Entomb"),
            mock.call("======"),
            mock.call(),
            mock.call(">> Files in .git directories are being included"),
            mock.call(),
            mock.call("Directory"),
            mock.call("---------"),
            mock.call("/tmp/entomb_testing"),
            mock.call(),
            mock.call("Operation"),
            mock.call("---------"),
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

        # Test a dry run for making all files in a directory immutable.
        with mock.patch("builtins.print") as mocked_print:
            core.main([EXECUTABLE, constants.DIRECTORY_PATH, "--dry-run"])
        expected = [
            mock.call(),
            mock.call("======"),
            mock.call("Entomb"),
            mock.call("======"),
            mock.call(),
            mock.call(">> This is a dry run so no changes will be made"),
            mock.call(),
            mock.call("Directory"),
            mock.call("---------"),
            mock.call("/tmp/entomb_testing"),
            mock.call(),
            mock.call("Operation"),
            mock.call("---------"),
            mock.call("Entomb objects"),
            mock.call(),
            mock.call("Progress"),
            mock.call("--------"),
            mock.call("-", end="\r"),
            mock.call("Entombed 0 of 1 files and ignored 0 links", end="\r"),
            mock.call("Entombed 0 of 1 files and ignored 1 links", end="\r"),
            mock.call("Entombed 1 of 2 files and ignored 1 links", end="\r"),
            mock.call("Entombed 1 of 3 files and ignored 1 links", end="\r"),
            mock.call("Entombed 1 of 3 files and ignored 2 links", end="\r"),
            mock.call("Entombed 2 of 4 files and ignored 2 links", end="\r"),
            mock.call(),
            mock.call(),
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Entombed 2 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("All 4 files are now entombed"),
            mock.call("All 2 links were ignored"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test making an immutable file mutable.
        with mock.patch("builtins.print") as mocked_print:
            core.main([EXECUTABLE, constants.IMMUTABLE_FILE_PATH, "--unset"])
        expected = [
            mock.call(),
            mock.call("======"),
            mock.call("Entomb"),
            mock.call("======"),
            mock.call(),
            mock.call("File"),
            mock.call("----"),
            mock.call("/tmp/entomb_testing/immutable.txt"),
            mock.call(),
            mock.call("Operation"),
            mock.call("---------"),
            mock.call("Unset objects"),
            mock.call(),
            mock.call("Progress"),
            mock.call("--------"),
            mock.call("-", end="\r"),
            mock.call("Unset 1 of 1 files and ignored 0 links", end="\r"),
            mock.call(),
            mock.call(),
            mock.call("Changes"),
            mock.call("-------"),
            mock.call("Unset 1 files"),
            mock.call(),
            mock.call("Summary"),
            mock.call("-------"),
            mock.call("All 1 files are now unset"),
            mock.call("All 0 links were ignored"),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__check_argument_conflicts(self):
        """Test the _check_argument_conflicts function.

        """
        # Test --dry-run and --report being passed in together.
        args = argparse.Namespace(
            dry_run=True,
            include_git=False,
            list_immutable=False,
            list_mutable=False,
            path=constants.DIRECTORY_PATH,
            report=True,
            unset=False,
        )
        actual = core._check_argument_conflicts(args)
        expected = ["--dry-run and --report cannot be passed together"]
        self.assertEqual(actual, expected)

        # Test --report and --unset being passed in together.
        args = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=False,
            list_mutable=False,
            path=constants.DIRECTORY_PATH,
            report=True,
            unset=True,
        )
        actual = core._check_argument_conflicts(args)
        expected = ["--report and --unset cannot be passed together"]
        self.assertEqual(actual, expected)

        # Test --list-immutable and --unset being passed in together.
        args = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=True,
            list_mutable=False,
            path=constants.DIRECTORY_PATH,
            report=False,
            unset=True,
        )
        actual = core._check_argument_conflicts(args)
        expected = ["--list-immutable and --unset cannot be passed together"]
        self.assertEqual(actual, expected)

        # Test --list-immutable, --list-mutable and --report being passed in
        # together.
        args = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=True,
            list_mutable=True,
            path=constants.DIRECTORY_PATH,
            report=True,
            unset=False,
        )
        actual = core._check_argument_conflicts(args)
        expected = [
            "--list-immutable and --list-mutable cannot be passed together",
            "--list-immutable and --report cannot be passed together",
            "--list-mutable and --report cannot be passed together",
        ]
        self.assertEqual(actual, expected)

        # Test --dry-run, --include-git, --list-mutable and --unset being
        # passed in together.
        args = argparse.Namespace(
            dry_run=True,
            include_git=True,
            list_immutable=False,
            list_mutable=True,
            path=constants.DIRECTORY_PATH,
            report=False,
            unset=True,
        )
        actual = core._check_argument_conflicts(args)
        expected = [
            "--dry-run and --list-mutable cannot be passed together",
            "--list-mutable and --unset cannot be passed together",
        ]
        self.assertEqual(actual, expected)

        # Test --unset be passed in alone.
        args = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=False,
            list_mutable=False,
            path=constants.DIRECTORY_PATH,
            report=False,
            unset=True,
        )
        actual = core._check_argument_conflicts(args)
        expected = []
        self.assertEqual(actual, expected)

        # Test no optional arguments being passed in.
        args = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=False,
            list_mutable=False,
            path=constants.DIRECTORY_PATH,
            report=False,
            unset=False,
        )
        actual = core._check_argument_conflicts(args)
        expected = []
        self.assertEqual(actual, expected)

    def test__get_absolute_path(self):
        """Test the _get_absolute_path function.

        """
        # Test an absolute path.
        actual = core._get_absolute_path(constants.DIRECTORY_PATH)
        expected = constants.DIRECTORY_PATH
        self.assertEqual(actual, expected)

        # Test a relative path.
        actual = core._get_absolute_path(constants.RELATIVE_PATH)
        expected = os.path.join(os.getcwd(), constants.RELATIVE_PATH)
        self.assertEqual(actual, expected)

        # Test a path which contains a ".." reference.
        actual = core._get_absolute_path("/tmp/entomb_testing/..")
        expected = "/tmp"
        self.assertEqual(actual, expected)

        # Test a path which contains "." references.
        actual = core._get_absolute_path("/tmp/././entomb_testing")
        expected = "/tmp/entomb_testing"
        self.assertEqual(actual, expected)

    def test__get_path_type(self):
        """Test the _get_path_type function.

        """
        # Test a link.
        actual = core._get_path_type(constants.LINK_PATH)
        expected = "link"
        self.assertEqual(actual, expected)

        # Test a file.
        actual = core._get_path_type(constants.IMMUTABLE_FILE_PATH)
        expected = "file"
        self.assertEqual(actual, expected)

        # Test a directory.
        actual = core._get_path_type(constants.DIRECTORY_PATH)
        expected = "directory"
        self.assertEqual(actual, expected)

        # Test a relative path.
        with self.assertRaises(exceptions.ObjectTypeError):
            core._get_path_type(constants.RELATIVE_PATH)

        # Test a path which doesn't exist.
        with self.assertRaises(exceptions.PathDoesNotExistError):
            core._get_path_type(constants.NON_EXISTENT_PATH)

    def test__parse_args(self):
        """Test the _parse_args function.

        """
        # Test just a directory path.
        actual = core._parse_args([EXECUTABLE, constants.DIRECTORY_PATH])
        expected = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=False,
            list_mutable=False,
            path=constants.DIRECTORY_PATH,
            report=False,
            unset=False,
        )
        self.assertEqual(actual, expected)

        # Test a link path with --list--immutable and --u.
        actual = core._parse_args(
            [EXECUTABLE, constants.LINK_PATH, "--list-immutable", "-u"],
        )
        expected = argparse.Namespace(
            dry_run=False,
            include_git=False,
            list_immutable=True,
            list_mutable=False,
            path=constants.LINK_PATH,
            report=False,
            unset=True,
        )
        self.assertEqual(actual, expected)

        # Test --version without a path.
        output = io.StringIO
        with mock.patch("sys.stdout", new_callable=output) as mocked_stdout:
            # Stop stderr being displayed.
            with mock.patch("sys.stderr") as _:
                # Stop the test exiting before it can complete.
                with mock.patch("sys.exit") as _:
                    core._parse_args([EXECUTABLE, "--version"])
        actual = mocked_stdout.getvalue()
        self.assertRegex(actual, r"^Entomb \d+\.\d+\.\d+\n$")

    def test__print_argument_conflict_errors(self):
        """Test the _print_argument_conflict_errors function.

        """
        # Test a list with two error messages.
        with mock.patch("builtins.print") as mocked_print:
            core._print_argument_conflict_errors(
                ["Message one", "Message two"],
            )
        expected = [
            mock.call(),
            mock.call("ERROR:", "Message one"),
            mock.call("ERROR:", "Message two"),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a list with no error messages.
        with mock.patch("builtins.print") as mocked_print:
            core._print_argument_conflict_errors([])
        expected = [
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__print_path_not_found_error(self):
        """Test the _print_path_not_found_error function.

        """
        # Test a relative and absolute path.
        with mock.patch("builtins.print") as mocked_print:
            core._print_path_not_found_error(
                "immutable.txt",
                constants.IMMUTABLE_FILE_PATH,
            )
        expected = [
            mock.call(),
            mock.call("ERROR: The path you gave could not be found"),
            mock.call(">> You entered this path:", "immutable.txt"),
            mock.call(
                ">> It was expanded to this:",
                constants.IMMUTABLE_FILE_PATH,
            ),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test an absolute path.
        with mock.patch("builtins.print") as mocked_print:
            core._print_path_not_found_error(
                constants.IMMUTABLE_FILE_PATH,
                constants.IMMUTABLE_FILE_PATH,
            )
        expected = [
            mock.call(),
            mock.call("ERROR: The path you gave could not be found"),
            mock.call(
                ">> You entered this path:",
                constants.IMMUTABLE_FILE_PATH,
            ),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__prompt_for_sudo(self):
        """Test the _prompt_for_sudo function.

        """
        # Get as close as possible to testing for a user without root
        # privileges by using a mock side effect to print the subprocess.run
        # call.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("subprocess.run") as mocked_run:
                mocked_run.side_effect = print
                core._prompt_for_sudo()
        expected = [
            mock.call(),
            mock.call("** To set or unset files' immutable attributes, root"),
            mock.call("** privileges are required."),
            mock.call(),
            mock.call(["sudo", "-v"], check=True, stderr=-2, stdout=-3),
            mock.call(),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__signal_handler(self):
        """Test the _signal_handler function.

        """
        # Test a keyboard interrupt signal.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("sys.exit") as mocked_exit:
                mocked_exit.side_effect = print
                core._signal_handler(signal.SIGINT, None)
        expected = [
            mock.call(),
            mock.call(),
            mock.call(">> Keyboard interrupt signal received. Exiting."),
            mock.call(),
            mock.call(1),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

        # Test a termination signal.
        with mock.patch("builtins.print") as mocked_print:
            with mock.patch("sys.exit") as mocked_exit:
                mocked_exit.side_effect = print
                core._signal_handler(signal.SIGTERM, None)
        expected = [
            mock.call(),
            mock.call(),
            mock.call(">> Termination signal received. Exiting."),
            mock.call(),
            mock.call(1),
        ]
        self.assertEqual(mocked_print.mock_calls, expected)

    def test__user_has_root_privileges(self):
        """Test the _user_has_root_privileges function.

        """
        # Test for a user with root privileges.
        self.assertTrue(core._user_has_root_privileges())

        # Test for a user without root privileges by mocking a
        # CalledProcessError.
        with mock.patch("subprocess.run") as mocked_run:
            mocked_run.side_effect = subprocess.CalledProcessError(
                cmd=["sudo", "-ln"],
                returncode=1,
            )
            self.assertFalse(core._user_has_root_privileges())

    def tearDown(self):
        """Delete temporary directories and files.

        """
        helpers.tear_down()
