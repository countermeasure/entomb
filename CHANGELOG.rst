=========
Changelog
=========


Unreleased
----------

Added
~~~~~
- Added Python 3.9 support.

Changed
~~~~~~~
- Reordered items in the report and hid items when not relevant.


v0.3.1
------
*23 August 2020*

Fixed
~~~~~
- Clear progress bar before printing a path when listing files.
- Stopped crash caused by special files and files with certain permissions.


v0.3.0
------
*07 July 2020*

Added
~~~~~
- Added link count to report.
- Added progress bar.

Fixed
~~~~~
- Hide the cursor when it's not needed.


v0.2.1
------
*06 June 2020*

Fixed
~~~~~
- Stopped crash caused by running the application with no arguments.


v0.2.0
------
*03 June 2020*

Added
~~~~~
- Added ``--version`` / ``-v`` argument.

Fixed
~~~~~
- Exit gracefully on keyboard interrupt (``CTRL`` + ``C``) and termination
  signals.


v0.1.0
------
*30 May 2020*

- Initial release.
