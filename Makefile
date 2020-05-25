ci: lint
		@echo; \
		echo "** For the tests to set or unset temporary test files'"; \
		echo "** immutable attributes, root privileges are required."; \
		echo; \
		tox

coverage:
		@coverage report -m

init:
		@pip install -r requirements.txt

lint:
		@echo "Running Flake8"; \
		flake8; \
		echo "Running isort"; \
		isort **/*.py -c; \
		echo "Running pydocstyle"; \
		pydocstyle; \
		echo "Running Pylint"; \
		pylint entomb.py; \
		pylint entomb/.; \
		pylint --disable=duplicate-code,protected-access tests/.

test:
		@echo; \
		echo "** For the tests to set or unset temporary test files'"; \
		echo "** immutable attributes, root privileges are required."; \
		echo; \
		coverage run -m unittest

