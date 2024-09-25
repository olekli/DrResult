.PHONY: test format

default: format test

format:
	poetry run black -S drresult test

test:
	poetry run pytest
	poetry run mypy drresult test --enable-incomplete-feature=NewGenericSyntax
