.PHONY: test

test:
	poetry run pytest
	poetry run mypy drresult test --enable-incomplete-feature=NewGenericSyntax
