# Otter Password Manager — Documentation

Otter Password Manager consists of a Unity client and an independent REST backend.
The backend stores data in SQLite, authenticates users with JWT, and encrypts vault
passwords using AES-256-GCM.

## Documentation index

- [Architecture](architecture.md) — components, layers, dependencies, and diagrams.
- [Backend](backend.md) — startup, code structure, logging, and tests.
- [Unity client](unity-client.md) — UI, REST client, and application startup.
- [REST API](api.md) — endpoints, data formats, and examples.
- [Database](database.md) — SQLite, schema, backups, and recovery.
- [Security](security.md) — Argon2, JWT, AES-GCM, and secret management.
- [Configuration](configuration.md) — all `.env` variables.
- [Deployment](deployment.md) — example VPS deployment and diagnostics.

[Polska wersja](../pl/README.md)

## Quick start

Start the backend without activating a PowerShell script:

```powershell
cd "D:\Unity Projekty\OtterPasswordManager\backend"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m otter_password_manager
```

After startup, the following URLs are available:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Open the Unity scene and press **Play**. The interface is created automatically and
the local client connects to `http://127.0.0.1:8000`.

## Current implementation

The project includes registration, login, JWT, vault CRUD, entry encryption,
database migrations, and a simple Unity UI. A refresh token is returned during
login, but there is no endpoint for exchanging it for a new access token yet.

> **Production warning:** `/api/v1/users` endpoints do not enforce roles and must
> not be exposed publicly until administrator authorization is implemented.

