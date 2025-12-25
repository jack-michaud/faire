
run-services-eval:
	uv run python -m jack-software.evals.writing_services .

read-eval-results:
	uv run python -m jack-software.evals.hidden_logger
