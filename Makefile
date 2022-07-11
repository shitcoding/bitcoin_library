test:
	poetry run pytest

lint:
	poetry run flake8 py_bitcoin

selfcheck:
	poetry check

check: selfcheck test lint

install:
	poetry install

build: check
	-@rm ./dist/* 2> /dev/null
	poetry build

package-install: install build
	python3 -m pip install --user dist/*.whl

.PHONY:	test lint selfcheck check install build package-install
