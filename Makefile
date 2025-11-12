# Makefile for KSeF Client (Odoo 18)

DOCKER_COMPOSE ?= docker compose
CBASE := compose/docker-compose.base.yml
CDEV := compose/docker-compose.dev.yml
CTEST := compose/docker-compose.test.yml
CPROD := compose/docker-compose.prod.yml

# Default database name used for shell/update tasks (change as needed)
DB ?= odoo

.PHONY: help dev-up dev-down dev-restart dev-build logs shell update-module lint format test ci prod-build prod-up prod-down clean clean-volumes rebuild

help:
	@echo "KSeF Client – common tasks"
	@echo "\nDev:"
	@echo "  make dev-up         # start dev stack (build + up)"
	@echo "  make dev-down       # stop dev stack"
	@echo "  make dev-restart    # restart dev stack"
	@echo "  make dev-build      # rebuild dev image"
	@echo "  make logs           # follow Odoo logs"
	@echo "  make shell          # open Odoo shell (requires DB: $(DB))"
	@echo "  make update-module  # -u ksef_client in DB=$(DB)"
	@echo "  make lint           # run ruff in dev container"
	@echo "  make format         # run ruff format in dev container"
	@echo "\nTests/CI:"
	@echo "  make test           # run test overlay (lint + pytest)"
	@echo "  make ci             # alias for test"
	@echo "\nProduction:"
	@echo "  make prod-build     # build prod image (multi-stage)"
	@echo "  make prod-up        # run prod overlay"
	@echo "  make prod-down      # stop prod overlay"
	@echo "\nCleanup:"
	@echo "  make clean          # stop all stacks"
	@echo "  make clean-volumes  # stop and remove volumes"
	@echo "  make rebuild        # rebuild dev image (no cache)"

# ---- Development ----
dev-up:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) up -d --build

dev-down:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) down

dev-restart: dev-down dev-up

dev-build:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) build --no-cache odoo

logs:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) logs -f odoo

shell:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) exec odoo odoo shell --config /etc/odoo/odoo.conf -d $(DB)

update-module:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) exec odoo odoo -c /etc/odoo/odoo.conf -u ksef_client -d $(DB) --stop-after-init

lint:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) exec odoo ruff check --no-cache /mnt/extra-addons/ksef_client

format:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) exec odoo ruff format /mnt/extra-addons/ksef_client

# ---- Tests / CI ----
test ci:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CTEST) up --abort-on-container-exit --build ; \
	RET=$$? ; \
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CTEST) down -v ; \
	exit $$RET

# ---- Production ----
prod-build:
	docker build --target=prod -t ksef_client:prod -f docker/odoo/Dockerfile .

prod-up:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CPROD) up -d --build

prod-down:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CPROD) down

# ---- Cleanup / Utilities ----
clean:
	-$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) down || true
	-$(DOCKER_COMPOSE) -f $(CBASE) -f $(CTEST) down || true
	-$(DOCKER_COMPOSE) -f $(CBASE) -f $(CPROD) down || true

clean-volumes:
	-$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) down -v || true
	-$(DOCKER_COMPOSE) -f $(CBASE) -f $(CTEST) down -v || true
	-$(DOCKER_COMPOSE) -f $(CBASE) -f $(CPROD) down -v || true

rebuild:
	$(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) build --no-cache odoo && $(DOCKER_COMPOSE) -f $(CBASE) -f $(CDEV) up -d
