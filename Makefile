
run-services-eval:
	uv run python -m jack-software.evals.writing_services .

read-eval-results:
	uv run python -m jack-software.evals.hidden_logger

test-services-eval:
	cd jack-software && uv run python -m unittest evals.writing_services.test_ast_helpers -v
