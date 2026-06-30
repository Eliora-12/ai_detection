lint-python:
	flake8 python/ --max-line-length=120 --exclude=python/ai/model/ --ignore=E402,F401,E226,W503

lint-js:
	npx eslint app/ components/ lib/

type-check:
	npx tsc --noEmit

format-python:
	black python/ --line-length 120

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v --timeout=120

test-components:
	npm run test:components

check-all: lint-python lint-js type-check test-unit
