errors = E123,E203,E265,E266,E501,W503
origin := $(shell git config --get remote.origin.url)
formatPaths = alembic/ src/ tests/
testPaths = src/ tests/
imageName = josephine-wolf-oberholtzer/on-exactitude-in-science-api
gitCommit = $(shell git rev-parse HEAD)

help: ## This help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build:
	docker build -t ${imageName}:latest .
	docker build -t ${imageName}:${gitCommit} .

push: build
	docker login -u josephine-wolf-oberholtzer
	docker push ${imageName}:latest
	docker push ${imageName}:${gitCommit}

clean:
	find . -name '*.pyc' | xargs rm
	rm -Rif *.egg-info/
	rm -Rif .*cache/
	rm -Rif __pycache__
	rm -Rif build/
	rm -Rif dist/
	rm -Rif htmlcov/
	rm -Rif prof/
	rm -Rif wheelhouse/

lint: reformat ruff-lint mypy ## Run all linters

mypy:
	mypy --ignore-missing-imports ${formatPaths}

pytest:
	rm -Rf htmlcov/
	pytest \
		--cov-config=.coveragerc \
		--cov-report=html \
		--cov-report=term \
		--cov=src \
		--cov=tests \
		-vv \
		${testPaths}

test: pytest

reformat: ruff-imports-fix ruff-format-fix ## Reformat codebase

ruff-format: ## Lint via ruff
	ruff format --check --diff ${formatPaths}

ruff-format-fix: ## Lint via ruff
	ruff format ${formatPaths}

ruff-imports: ## Format imports via ruff
	ruff check --select I,RUF022 ${formatPaths}

ruff-imports-fix: ## Format imports via ruff
	ruff check --select I,RUF022 --fix ${formatPaths}

ruff-lint: ## Lint via ruff
	ruff check --diff ${formatPaths}

ruff-lint-fix: ## Lint via ruff
	ruff check --fix ${formatPaths}
