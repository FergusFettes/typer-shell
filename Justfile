set dotenv-load


install: reqs
	pip install --user -U .

build: reqs
	poetry build

publish: reqs clear
	poetry publish --build -u __token__ -p $PYPI_TOKEN

reqs:
	pip install poetry
	poetry export -f requirements.txt --without-hashes > requirements.txt

clear:
  rm -rf dist
