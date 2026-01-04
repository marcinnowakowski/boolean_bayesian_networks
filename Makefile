.PHONY: help install test lint format clean analyze docs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the project and dependencies
	poetry install

test: ## Run tests
	poetry run pytest tests/ -v

lint: ## Run linting
	poetry run flake8 boolean_networks/
	poetry run mypy boolean_networks/

format: ## Format code
	poetry run black boolean_networks/ tests/ examples/
	poetry run isort boolean_networks/ tests/ examples/

clean: ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf **/__pycache__/
	find . -name "*.pyc" -delete

visualize: ## Visualize a network (specify FILE=path)
	poetry run python -m boolean_networks.cli visualize $(FILE)

functions_to_truth_table: ## Generate truth table from functions (specify FILE=path, OUT=output)
	poetry run python -m boolean_networks.cli functions-to-truth-table $(FILE) $(if $(OUT),-o $(OUT),)

transitions_to_truth_table: ## Generate truth table from transitions (specify FILE=path, OUT=output)
	poetry run python -m boolean_networks.cli transitions-to-truth-table $(FILE) $(if $(OUT),-o $(OUT),)

truth_table_to_sops: ## Extract SOP functions from truth table (specify FILE=path, OUT=output)
	poetry run python -m boolean_networks.cli truth-table-to-sops $(FILE) $(if $(OUT),-o $(OUT),)

simplify_sops: ## Simplify SOP expressions (specify FILE=path, OUT=output)
	poetry run python -m boolean_networks.cli simplify-sops $(FILE) $(if $(OUT),-o $(OUT),)

generate_network: ## Generate 7D network (specify OUT=output, SEED=seed)
	poetry run python -m boolean_networks.cli generate-network $(if $(OUT),-o $(OUT),) $(if $(SEED),-s $(SEED),)

generate_3dep: ## Generate 7D network with 3-var limit (specify OUT=output, SEED=seed)
	poetry run python -m boolean_networks.cli generate-3dep $(if $(OUT),-o $(OUT),) $(if $(SEED),-s $(SEED),)

docs: ## Generate documentation (placeholder)
	@echo "Documentation generation not implemented yet"

check: test lint ## Run all checks

all: install format lint test ## Install, format, lint, and test