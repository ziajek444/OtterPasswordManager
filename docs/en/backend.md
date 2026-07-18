# FastAPI backend

[Polska wersja](../pl/backend.md)

## Requirements

- Python 3.13,
- the `backend/.venv` virtual environment,
- dependencies declared in `backend/pyproject.toml`.

## Installation

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\alembic.exe upgrade head
```

Activating `.venv` is optional. If PowerShell blocks `Activate.ps1`, invoke the
executables from `.venv\Scripts` directly.

## Starting the backend

```powershell
.\.venv\Scripts\python.exe -m otter_password_manager
```

Uvicorn reads the host, port, and reload settings from `.env`. Stop it with
`Ctrl+C`. Restarting the process does not remove SQLite data.

## Directory structure

```text
backend/
├── migrations/                 # Alembic environment and revisions
├── data/                       # local SQLite file
├── src/otter_password_manager/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   ├── main.py
│   └── __main__.py
├── tests/
├── .env                        # local secrets, ignored by Git
├── .env.example                # configuration template
├── alembic.ini
└── pyproject.toml
```

## Dependency injection

The project uses an explicit `ApplicationContainer` instead of an external DI
framework. FastAPI obtains it through `app.state.container`, and presentation
dependencies expose individual services. Tests can replace ports with fakes.

## Logging

`OTTER_LOG_FORMAT=console` produces readable text logs. `json` emits one JSON
object per line for log collectors. `OTTER_LOG_LEVEL` controls the level.

Never log credentials, vault passwords, JWTs, the encryption key, or the JWT secret.

## Tests and quality checks

```powershell
.\.venv\Scripts\ruff.exe check src migrations tests
.\.venv\Scripts\pytest.exe -q
```

Unit tests cover registration, login, JWT, middleware, encryption, and entry
ownership rules.

## Troubleshooting

- `ModuleNotFoundError`: use the interpreter from `backend/.venv` and reinstall.
- `no such table`: run `alembic upgrade head` from `backend`.
- `Address already in use`: change `OTTER_UVICORN_PORT` or stop the old process.
- settings validation error: compare `.env` with `.env.example`.
- `InvalidTag` while decrypting: the key differs from the original key or the data
  was modified.

