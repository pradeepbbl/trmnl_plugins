# Changelog

All notable changes to the Energy Pulse plugin are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.1] - 2026-09-15

### Changed

- Marketplace description, in-app plugin bio, and README now state upfront
  that coverage is ENTSO-E markets only (EU, UK, Norway, Switzerland) and
  that the US / other regions aren't supported, to set expectations before
  install.
- Added `help_text` to the bidding zone setting pointing out the same scope
  for installers who can't find their country in the list.
- Great Britain is now 14 selectable GSP regions (Octopus Agile tariff
  areas) instead of one flat "Great Britain" option, so installers get
  their own region's rates instead of always London's. Backed by the
  GB Octopus Agile fallback, which now takes the region per request 
  instead of a single hardcoded default.

## [1.0.0] - 2026-08-22

### Added

- Initial release of Energy Pulse: today's hourly day-ahead electricity
  prices for a European bidding zone, sourced from the ENTSO-E Transparency
  Platform.
- Four layouts — `full`, `half_horizontal`, `half_vertical`, and `quadrant`
  — with past/current/future hour styling and today's average line.
- `full` layout usage-examples row showing what common loads cost now vs.
  at the cheapest hour still to come.
- Settings for bidding zone (26 zones), price unit
  (`currency_kwh` / `subunit_kwh` / `currency_mwh`), custom usage examples,
  and optional VAT %.
- Handling for mixed `PT15M`/`PT60M` publication resolutions, DST
  transitions, negative prices, and fetch/parse failures.

[Unreleased]: https://github.com/pradeepbbl/trmnl_plugins/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/pradeepbbl/trmnl_plugins/releases/tag/v1.0.1
[1.0.0]: https://github.com/pradeepbbl/trmnl_plugins/releases/tag/v1.0.0
