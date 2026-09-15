# Docker-based trmnlp workflow for this monorepo.
#
# Usage:
#   make serve PLUGIN=energy_pulse          # http://localhost:4567
#   make lint PLUGIN=energy_pulse
#   make build PLUGIN=energy_pulse
#   make pull PLUGIN=energy_pulse
#
# Requires Docker only — no local Ruby install.

IMAGE := trmnl/trmnlp
PORT  ?= 4567

ifeq ($(filter help,$(MAKECMDGOALS)),)
ifndef PLUGIN
$(error PLUGIN is required, e.g. make lint PLUGIN=energy_pulse)
endif
endif

DOCKER_RUN := docker run --rm --pull always --net=host \
	--volume "$(CURDIR)/$(PLUGIN):/plugin"

.PHONY: help serve build lint pull test

help:
	@echo "Targets: serve build lint pull test  (pass PLUGIN=<dir>, e.g. PLUGIN=energy_pulse)"

serve: ## Start the live-reload preview server
	$(DOCKER_RUN) --publish $(PORT):4567 $(IMAGE) serve

build: ## Render static HTML/PNG output to $(PLUGIN)/_build
	$(DOCKER_RUN) $(IMAGE) build

lint: ## Validate the plugin against trmnlp's best-practice checks
	$(DOCKER_RUN) $(IMAGE) lint

pull: ## Download the plugin's current state from TRMNL
	$(DOCKER_RUN) $(IMAGE) pull

