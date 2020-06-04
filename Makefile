# /!\ /!\ /!\ /!\ /!\ /!\ /!\ DISCLAIMER /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# This Makefile is only meant to be used for DEVELOPMENT purpose as we are
# changing the user id that will run in the container.
#
# PLEASE DO NOT USE IT FOR YOUR CI/PRODUCTION/WHATEVER...
#
# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# Note to developpers:
#
# While editing this file, please respect the following statements:
#
# 1. Every variable should be defined in the ad hoc VARIABLES section with a
#    relevant subsection
# 2. Every new rule should be defined in the ad hoc RULES section with a
#    relevant subsection depending on the targeted service
# 3. Rules should be sorted alphabetically within their section
# 4. When a rule has multiple dependencies, you should:
#    - duplicate the rule name to add the help string (if required)
#    - write one dependency per line to increase readability and diffs
# 5. .PHONY rule statement should be written after the corresponding rule
# ==============================================================================
# VARIABLES

# -- Database

DB_HOST            = postgresql
DB_PORT            = 5432

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker-compose
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_RUN_APP      = $(COMPOSE_RUN) django-lti-toolbox
COMPOSE_TEST_RUN     = $(COMPOSE_RUN)
COMPOSE_TEST_RUN_APP = $(COMPOSE_TEST_RUN) django-lti-toolbox
MANAGE               = $(COMPOSE_RUN_APP) python sandbox/manage.py
WAIT_DB              = @$(COMPOSE_RUN) dockerize -wait tcp://$(DB_HOST):$(DB_PORT) -timeout 60s

# ==============================================================================
# RULES

default: help

# -- Project

bootstrap: ## Prepare Docker images for the project
bootstrap: \
	build \
	migrate
.PHONY: bootstrap

# -- Docker/compose
build: ## build the app container
	@$(COMPOSE) build django-lti-toolbox
.PHONY: build

down: ## stop and remove containers, networks, images, and volumes
	@$(COMPOSE) down
.PHONY: down

logs: ## display app logs (follow mode)
	@$(COMPOSE) logs -f django-lti-toolbox
.PHONY: logs

run: ## start the development server using Docker
	@$(COMPOSE) up -d
	@echo "Wait for postgresql to be up..."
	@$(WAIT_DB)
.PHONY: run

status: ## an alias for "docker-compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop the development server using Docker
	@$(COMPOSE) stop
.PHONY: stop

# -- Backend

# Nota bene: Black should come after isort just in case they don't agree...
lint: ## lint back-end python sources
lint: \
  lint-isort \
  lint-black \
  lint-flake8 \
  lint-mypy \
  lint-pylint \
  lint-bandit
.PHONY: lint

lint-bandit: ## lint back-end python sources with bandit
	@echo 'lint:bandit started…'
	@$(COMPOSE_TEST_RUN_APP) bandit -qr src sandbox
.PHONY: lint-bandit

lint-black: ## lint back-end python sources with black
	@echo 'lint:black started…'
	@$(COMPOSE_TEST_RUN_APP) black src sandbox tests
.PHONY: lint-black

lint-flake8: ## lint back-end python sources with flake8
	@echo 'lint:flake8 started…'
	@$(COMPOSE_TEST_RUN_APP) flake8
.PHONY: lint-flake8

lint-isort: ## automatically re-arrange python imports in back-end code base
	@echo 'lint:isort started…'
	@$(COMPOSE_TEST_RUN_APP) isort --recursive --atomic .
.PHONY: lint-isort

lint-mypy: ## type check back-end python sources with mypy
	@echo 'lint:mypy started…'
	@$(COMPOSE_TEST_RUN_APP) mypy src
.PHONY: lint-mypy

lint-pylint: ## lint back-end python sources with pylint
	@echo 'lint:pylint started…'
	@$(COMPOSE_TEST_RUN_APP) pylint src sandbox tests
.PHONY: lint-pylint

test: ## run back-end tests
	@$(COMPOSE_TEST_RUN_APP) pytest
.PHONY: test

migrate:  ## run django migration for the sandbox project.
	@echo "$(BOLD)Running migrations$(RESET)"
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(MANAGE) migrate
.PHONY: migrate


# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
