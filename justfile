build-exe:
    pyinstaller --onefile s4-gen.py

setup:
    python3 -m pip install -r requirements.txt

clean:
    rm -r -f dist

build: clean setup
    python3 -m build

install: build
    python3 -m pip install --force-reinstall ./dist/*.whl
