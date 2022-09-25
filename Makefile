
typecheck:
	poetry run mypy color_grep/

test:
	poetry run pytest tests/
