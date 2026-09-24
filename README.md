# trmnl_plugins

Monorepo for [TRMNL](https://usetrmnl.com) plugins. Each top-level directory
is a self-contained plugin (Liquid views + `settings.yml` + its own README);
CI auto-discovers any directory with a `.trmnlp.yml` and lints/pushes it
independently.

## Plugins

| Plugin | Description |
| --- | --- |
| [`energy_pulse`](energy_pulse/README.md) | Day-ahead hourly electricity prices for a European bidding zone. |
| [`apple_health`](apple_health/README.md) | Steps, active energy, sleep, heart rate, and today's workouts from Apple Health, synced via the TRMNL Companion app. |

## Development

All plugin work runs through `trmnlp` in Docker via the root `Makefile` — no
local Ruby install needed:

```bash
make serve PLUGIN=energy_pulse    # live-reload preview, http://localhost:4567
make lint PLUGIN=energy_pulse     # validate against trmnlp best practices
make build PLUGIN=energy_pulse    # render static output to <plugin>/_build
```

`PLUGIN` is required for every target. See each plugin's own README for
plugin-specific settings and data sources.

## CI

`.github/workflows/trmnl.yml` finds every plugin directory, runs `trmnlp
lint` on each in a matrix, and — on push to `master` — runs `trmnlp push
--force` for each, authenticated via the `TRMNL_API_KEY` repo secret.
