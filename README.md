# Portfolio data workspace

This repository is the single persisted-data root shared by the portfolio packages. Public,
reproducible market data is committed; personal transactions, crypto state, real-estate data,
runtime output, credentials, and chain configuration stay local through `.gitignore`.

## Setup

This is the end-user/release environment. Its lockfile resolves immutable package tags and must
never contain editable paths to source repositories. Regenerate it with `uv lock --no-sources`
after changing a package tag:

```powershell
uv sync --frozen
uv run portfolio-market --help
uv run portfolio-crypto --help
```

Loader commands use the installed packages:

```powershell
uv run portfolio-market --data-dir . prices update
uv run portfolio-market --data-dir . transactions update
uv run portfolio-crypto --data-dir . update
```

The installed dashboard can also point at this directory. `portfolio.toml` declares the data
contract version. Put `GETQUIN_TOKEN` in `.env`; credential files are not supported.

`scripts/validate_workspace.py` rejects tracked private-data paths and local dependency sources.
Both CI and the scheduled price workflow run it before accepting generated changes.

Even when all source repositories are present on the same computer, do not add
`[tool.uv.sources]` here. Use the dashboard checkout and `scripts/test-all.ps1` for editable
development. Keeping this environment tag-backed makes it a useful end-user installation test.

Virtual environments use uv's centralized cache under `%LOCALAPPDATA%\uv`, so OneDrive does not
need to synchronize package files. `.venv` is only a junction to that cache.
