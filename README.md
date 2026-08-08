# Portfolio data workspace

This repository is the single persisted-data root shared by the portfolio packages. Public,
reproducible market data is committed; personal transactions, crypto state, real-estate data,
runtime output, credentials, and chain configuration stay local through `.gitignore`.

## Setup

```powershell
uv sync
uv run portfolio-market --data-dir . prices update
uv run portfolio-market --data-dir . transactions update
uv run portfolio-crypto --data-dir . update
```

The installed dashboard can also point at this directory. `portfolio.toml` declares the data
contract version. Put `GETQUIN_TOKEN` in `.env`; credential files are not supported.

`scripts/validate_workspace.py` rejects tracked private-data paths and local dependency sources.
Both CI and the scheduled price workflow run it before accepting generated changes.

Virtual environments use uv's centralized cache under `%LOCALAPPDATA%\uv`, so OneDrive does not
need to synchronize a `.venv` directory.
