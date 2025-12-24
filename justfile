build-exe:
	#!/usr/bin/env sh
	source .venv/bin/activate
	pip3 install --force-reinstall ./dist/*.whl
	pyinstaller --onefile src/cli/cli.py --collect-submodules s4_gen

setup:
	#!/usr/bin/env sh
	python3 -m venv .venv
	source .venv/bin/activate
	pip3 install -r requirements.txt

clean:
	rm -r -f dist

build: clean setup
	#!/usr/bin/env sh
	source .venv/bin/activate
	python3 -m build

install: build
	pip3 install --force-reinstall ./dist/*.whl

test: build
	#!/usr/bin/env sh
	source .venv/bin/activate
	pip3 install --force-reinstall ./dist/*.whl
	cd ./test
	python3 ../src/cli/cli.py build
