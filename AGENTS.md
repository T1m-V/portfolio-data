# AGENTS.md

## Purpose

`portfolio-data` is the single external runtime workspace for the portfolio system. It is not a
Python package (`tool.uv.package = false`). Its uv environment installs the two loader applications;
the dashboard is configured to read this directory separately.

## System Relationships

| Package/application | Reads from this workspace | Writes to this workspace |
| --- | --- | --- |
| `portfolio-core` | `portfolio.toml`, `config/`, prices, and settings/secrets | User configuration is stored outside this repo; shared price helpers may write only when called by a loader. |
| `portfolio-market-data` | Metadata and existing prices/transactions | `prices/`, `latest_prices.csv`, and `transactions/`. |
| `portfolio-crypto-data` | `config/chains.json`, prices, crypto transactions, and existing state | `crypto/`, LP prices, accounting output, and dashboard artifacts. |
| `portfolio-dashboard` | Metadata, prices, transactions, crypto artifacts, and real-estate data | No direct writes; explicit refresh jobs delegate to the installed loaders. |
| GitHub Actions | `pyproject.toml`, `uv.lock`, and tracked market data | Runs `portfolio-market ... prices update` and commits changed tracked price CSVs. |

The installed dependency direction is core -> market/crypto. The dashboard depends on all three,
but this workspace intentionally does not install the dashboard.

## Workspace Layout

- `portfolio.toml`: data schema marker; currently `schema_version = 1`.
- `config/stock_metadata.json`, `config/currency_metadata.json`: tracked shared metadata.
- `prices/`, `latest_prices.csv`: tracked, reproducible market data.
- `transactions/`: private Getquin exports and derived snapshots; ignored.
- `crypto/`: private chain transactions, protocol state, accounting output, and artifacts; ignored.
- `real_estate/`: private user-maintained data; ignored.
- `runtime/`: disposable runtime output; ignored.
- `.env`, `config/getquin-token.txt`, `config/chains.json`: private credentials/configuration;
  ignored.

Never add ignored private paths with `git add -f`. Before committing, confirm that no credential,
transaction, wallet, chain configuration, or real-estate file is tracked.

## Refactoring Policy

- Optimize the whole system for the new layout; do not preserve the former monorepo `data/`
  structure.
- When a layout or CSV contract changes, update `portfolio-core`, every writer, every reader, the
  workflow, tests, and documentation together.
- Increment `schema_version` for a breaking persisted-data change.
- Prefer a focused one-way migration over permanent dual-directory lookup or old/new column
  support.
- Do not add symlinks, duplicate data trees, compatibility copies, or fallback searches for old
  locations unless explicitly requested.
- Avoid unnecessary CSV churn. A refactor should not rewrite tracked prices when their values and
  canonical format are unchanged.
- Generated data is not source code. Change the responsible package rather than patching output by
  hand, except for an explicit data-repair task.

The goal is coordinated breaking change, not compatibility accumulation. Package tags and lockfiles
make the coordinated state reproducible.

## Dependency And Release Updates

`pyproject.toml` pins `portfolio-core`, `portfolio-market-data`, and `portfolio-crypto-data` to
published Git tags. When upgrading:

1. Release core first when needed.
2. Release market and crypto against that core tag.
3. Update all three Git tags here.
4. Run `uv lock` and inspect `uv.lock` for Git URLs and immutable commit SHAs; no `file://` or local
   path source may remain.
5. Run a clean `uv sync --frozen` before committing.

Never move a published release tag. Use a new package/workspace version.

## Safe Commands

```powershell
uv sync --frozen
uv run portfolio-market --help
uv run portfolio-crypto --help
```

The following commands call external services and mutate data. Run them only when the user
explicitly requests a refresh:

```powershell
uv run portfolio-market --data-dir . prices update
uv run portfolio-market --data-dir . transactions update
uv run portfolio-crypto --data-dir . update
uv run portfolio-crypto --data-dir . rebuild
```

## Environment And OneDrive

Use uv's `centralized-project-envs` feature. The real environment belongs under
`%LOCALAPPDATA%\uv\cache\environments-v2`; `.venv` in this OneDrive workspace is only a junction and
is ignored by Git. Do not copy or commit an environment. If OneDrive marks generated cache entries
read-only, repair only the exact uv environment after verifying its resolved target.

## Validation Before Commit

- `git status --short --ignored` shows private directories as ignored.
- `git ls-files` contains only intended metadata, workflow/configuration, documentation, and public
  market data.
- `uv sync --frozen` succeeds without local path dependencies.
- Price files remain canonical and `latest_prices.csv` retains `date, isin, price`.
- No loader command was run unintentionally.
