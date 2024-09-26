.PHONY: test format

default: format test

format:
	poetry run black \
		--skip-string-normalization \
		--line-length 100 \
			drresult test

test:
	poetry run pytest
	poetry run mypy drresult test \
		--enable-incomplete-feature=NewGenericSyntax
