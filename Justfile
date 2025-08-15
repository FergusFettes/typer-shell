set dotenv-load


install:
	pip install --user -U .

build:
	poetry build

publish: clear
	poetry publish --build -u __token__ -p $PYPI_TOKEN

clear:
  rm -rf dist
