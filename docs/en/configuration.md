# Configuration

[Polska wersja](../pl/configuration.md)

The backend uses `pydantic-settings`. It reads `backend/.env`, while process
environment variables take precedence. Every variable uses the `OTTER_` prefix.

## Backend variables

| Variable | Example | Meaning |
|---|---|---|
| `OTTER_APP_NAME` | `Otter Password Manager API` | OpenAPI application name |
| `OTTER_ENVIRONMENT` | `development` | `development`, `testing`, or `production` |
| `OTTER_DEBUG` | `false` | FastAPI debug and SQLAlchemy echo |
| `OTTER_API_PREFIX` | `/api/v1` | Technical Users API prefix |
| `OTTER_DATABASE_URL` | `sqlite+aiosqlite:///./data/otter_password_manager.db` | SQLAlchemy URL |
| `OTTER_LOG_LEVEL` | `INFO` | Logging level |
| `OTTER_LOG_FORMAT` | `console` | `console` or `json` |
| `OTTER_JWT_SECRET` | no safe default | JWT signing secret, at least 32 characters |
| `OTTER_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access-token lifetime |
| `OTTER_REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh-token lifetime |
| `OTTER_ENCRYPTION_KEY` | no safe default | 32 bytes encoded as URL-safe Base64 |
| `OTTER_UVICORN_HOST` | `127.0.0.1` | Listening interface |
| `OTTER_UVICORN_PORT` | `8000` | Port in the range 1–65535 |
| `OTTER_UVICORN_RELOAD` | `true` locally | Reload process after code changes |

`.env.example` is a version-controlled template. `.env` contains secrets and is
ignored by Git.

## Local example

```dotenv
OTTER_ENVIRONMENT=development
OTTER_DEBUG=false
OTTER_DATABASE_URL=sqlite+aiosqlite:///./data/otter_password_manager.db
OTTER_LOG_LEVEL=INFO
OTTER_LOG_FORMAT=console
OTTER_JWT_SECRET=<random-secret>
OTTER_ACCESS_TOKEN_EXPIRE_MINUTES=15
OTTER_REFRESH_TOKEN_EXPIRE_DAYS=30
OTTER_ENCRYPTION_KEY=<32-byte-base64-key>
OTTER_UVICORN_HOST=127.0.0.1
OTTER_UVICORN_PORT=8000
OTTER_UVICORN_RELOAD=true
```

## Production example

```dotenv
OTTER_ENVIRONMENT=production
OTTER_DEBUG=false
OTTER_DATABASE_URL=sqlite+aiosqlite:////opt/otter-password-manager/backend/data/otter_password_manager.db
OTTER_LOG_LEVEL=INFO
OTTER_LOG_FORMAT=json
OTTER_JWT_SECRET=<unique-production-secret>
OTTER_ACCESS_TOKEN_EXPIRE_MINUTES=15
OTTER_REFRESH_TOKEN_EXPIRE_DAYS=30
OTTER_ENCRYPTION_KEY=<unique-production-key>
OTTER_UVICORN_HOST=127.0.0.1
OTTER_UVICORN_PORT=8000
OTTER_UVICORN_RELOAD=false
```

Four slashes after `sqlite:` denote an absolute Unix path.

## Unity configuration

The API URL is currently a constant in `ApplicationBootstrapper.cs`:

```csharp
private const string LocalApiUrl = "http://127.0.0.1:8000";
```

Inside a deployed build, `127.0.0.1` refers to the user's device, not the VPS.
Replace it with the public HTTPS URL before a production build. A future
`ApiConfiguration` ScriptableObject should provide environment profiles.

## Validation

An absent or short `OTTER_JWT_SECRET` prevents startup. `EncryptionService` rejects
invalid Base64 and decoded keys that are not exactly 32 bytes. Failing fast prevents
the application from starting with unsafe configuration.

