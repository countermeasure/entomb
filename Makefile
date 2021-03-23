ci: lint
	@echo
	@echo "** For the tests to set or unset temporary test files'"
	@echo "** immutable attributes, root privileges are required."
	@echo
	@tox

clean:
	@rm -rf build/ dist/

coverage: test
	@coverage report -m

help:
	@echo
	@echo "  make ci          Run continuous integration checks locally."
	@echo "  make clean       Clean up after making a package."
	@echo "  make coverage    Generate a test coverage report."
	@echo "  make help        Show this help."
	@echo "  make init        Install development dependencies."
	@echo "  make install     Install Entomb in editable mode."
	@echo "  make lint        Lint the code."
	@echo "  make package     Build the package."
	@echo "  make push        Push the main branch to the repo."
	@echo "  make release     Release to PyPI."
	@echo "  make tag         Make the Git tag for the release."
	@echo "  make test        Run the tests in the development environment."

init:
	@pip install -r requirements.txt

install:
	@pip install -e .

lint:
	@echo "Running Flake8"
	@flake8
	@echo "Running isort"
	@isort **/*.py -c
	@echo "Running pydocstyle"
	@pydocstyle
	@echo "Running Pylint"
	@pylint *.py
	@pylint entomb/.
	@pylint --disable=duplicate-code,protected-access,too-many-statements \
		tests/.
	@echo "Running twine check"
	@python setup.py sdist > /dev/null
	@twine check dist/*
	@rm -rf build/ dist/ entomb.egg-info/

package:
	@python setup.py sdist bdist_wheel

publish:
	@twine upload dist/*

push:
	@git checkout main
	@git push origin main
	@git push origin v`python setup.py --version`

release:
	@git add CHANGELOG.rst entomb/__init__.py
	@git commit -m "Release v`python setup.py --version`"
	@git tag \
		-a v`python setup.py --version` \
		-m "Entomb v`python setup.py --version`"

test:
	@echo
	@echo "** For the tests to set or unset temporary test files'"
	@echo "** immutable attributes, root privileges are required."
	@echo
	@coverage run -m unittest

.DEFAULT_GOAL:= help
.PHONY: ci clean coverage help init install lint package publish push release \
	test
