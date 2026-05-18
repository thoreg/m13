# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
make test                          # or: uv run pytest --import-mode=importlib --ds=m13.config.develop .

# Run a single test file or test
uv run pytest --import-mode=importlib --ds=m13.config.develop path/to/test.py::test_name

# Run tests verbosely
make testv

# Regenerate regression test traces (tests will fail afterwards)
make test_over

# Format & lint
make format    # ruff format + ruff check
make style     # flake8 + pylint

# Coverage
make py-cov
```

## Architecture

**m13** is a Django operations backend for a multi-marketplace e-commerce seller (Manufaktur13). It integrates with Zalando, Otto, Etsy, Galaxus, Galeria, AboutYou, and TikTok.

### Project layout

Each marketplace is its own Django app (`zalando/`, `otto/`, `etsy/`, etc.) with a consistent internal structure:
- `models.py` — marketplace-specific `Order`, `OrderItem`, `Address`, `Shipment` models (all extend `TimeStampedModel`)
- `services/` — all business logic; views and management commands call into here
- `views.py` / `viewsets.py` — thin HTTP layer
- `management/commands/` — CLI entry points named `m13_<marketplace>_<action>.py`; these are what cron jobs call
- `tests/` — integration tests using `@pytest.mark.django_db`; fixtures live in `tests/fixtures/`

### Core app (`core/`)

Central shared data:
- `Price` — SKU-keyed price table; single source of truth for pricing across all marketplaces (`vk_zalando`, `vk_otto`, `vk_aboutyou`, etc.)
- `Article` / `Product` / `Category` — product catalog
- `MarketplaceConfig` — per-marketplace cost configuration (shipping, return, provision, VAT); only one active config per marketplace at a time
- `Job` / `Error` — background job tracking; the dashboard (`/`) renders recent job runs and uncleared errors
- `SalesStatsTop13`, `SalesStatsReturnTop13`, `SalesVolumeZalando` — PostgreSQL materialized views via `django-pgviews`; refresh with `m13_update_materialized_views`

### URL routing

| Prefix | App |
|--------|-----|
| `/z/` | zalando |
| `/otto/` | otto |
| `/etsy/` | etsy |
| `/galaxus/` | galaxus |
| `/galeria/` | galeria |
| `/ay/` | aboutyou |
| `/tiktok/` | tiktok |
| `/shipping/` | shipping |
| `/api/` | DRF router (order items, sales stats) |
| `/addi/` | Django admin (massadmin) |

### Database

PostgreSQL. Dev config in `m13/config/develop.py` expects `postgres:local@127.0.0.1:5432/m13`.

### Testing conventions

- `conftest.py` at repo root defines a session-scoped `django_db_setup` that loads fixtures for otto and etsy
- Tests with `--overwrite` flag regenerate stored regression traces
- `core/unit_tests/` contains pure-unit tests (no DB); `<app>/tests/` contains integration tests
- Run with `--import-mode=importlib` (required — do not omit)

### Package management

Uses `uv`. Always prefix Python commands with `uv run`.

## Planning & Tasks

Implementation plans live in `docs/plans/` as Markdown files.

| Plan | Status |
|---|---|
| `docs/plans/zalando-pp-migration.md` | TODO — Zalando CR→PP Feed-Migration |
