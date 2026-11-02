PACKAGE_NAME=pelican/plugins/feed_minify

.PHONY: tests

# development & release cycle
fullrelease:
	fullrelease

check_setups:
	pyroma .

check_code:
	prospector $(PACKAGE_NAME)/
	check-manifest

clean:
	@echo Clean build files...
	rm -rf build/ dist/ *.egg-info .eggs/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

sdist: clean
	@echo Building the distribution package...
	python -m build --sdist

wheel: clean
	@echo Building the wheel package...
	python -m build --wheel

upload:
	@echo Building the distribution + wheel packages...
	python -m build
	twine upload dist/* -r pypi

# Tests
tests:
	python -m pytest tests -v

coverage:
	python -m pytest --cov=$(PACKAGE_NAME) --cov-report term-missing -vv
	@-coverage-badge -f -o images/coverage.svg

