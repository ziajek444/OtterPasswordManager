# Konfiguracja

[English version](../en/configuration.md)

Backend używa `pydantic-settings`. Odczytuje `backend/.env`, a następnie nadpisuje
wartości zmiennymi środowiskowymi. Wszystkie nazwy mają prefiks `OTTER_`.

## Zmienne backendu

| Zmienna | Domyślny przykład | Znaczenie |
|---|---|---|
| `OTTER_APP_NAME` | `Otter Password Manager API` | Nazwa w OpenAPI |
| `OTTER_ENVIRONMENT` | `development` | `development`, `testing` lub `production` |
| `OTTER_DEBUG` | `false` | Debug FastAPI i echo SQLAlchemy |
| `OTTER_API_PREFIX` | `/api/v1` | Prefix technicznego Users API |
| `OTTER_DATABASE_URL` | `sqlite+aiosqlite:///./data/otter_password_manager.db` | URL SQLAlchemy |
| `OTTER_LOG_LEVEL` | `INFO` | Poziom logowania |
| `OTTER_LOG_FORMAT` | `console` | `console` albo `json` |
| `OTTER_JWT_SECRET` | brak bezpiecznego defaultu | Sekret podpisu JWT, min. 32 znaki |
| `OTTER_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Żywotność access tokenu |
| `OTTER_REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Żywotność refresh tokenu |
| `OTTER_ENCRYPTION_KEY` | brak bezpiecznego defaultu | 32 bajty URL-safe Base64 |
| `OTTER_UVICORN_HOST` | `127.0.0.1` | Interfejs nasłuchu |
| `OTTER_UVICORN_PORT` | `8000` | Port 1–65535 |
| `OTTER_UVICORN_RELOAD` | `true` lokalnie | Automatyczny restart po zmianie kodu |

`.env.example` jest szablonem i może być wersjonowany. `.env` zawiera sekrety i
jest ignorowany przez Git.

## Przykład lokalny

```dotenv
OTTER_ENVIRONMENT=development
OTTER_DEBUG=false
OTTER_DATABASE_URL=sqlite+aiosqlite:///./data/otter_password_manager.db
OTTER_LOG_LEVEL=INFO
OTTER_LOG_FORMAT=console
OTTER_JWT_SECRET=<losowy-sekret>
OTTER_ACCESS_TOKEN_EXPIRE_MINUTES=15
OTTER_REFRESH_TOKEN_EXPIRE_DAYS=30
OTTER_ENCRYPTION_KEY=<32-bajtowy-klucz-base64>
OTTER_UVICORN_HOST=127.0.0.1
OTTER_UVICORN_PORT=8000
OTTER_UVICORN_RELOAD=true
```

## Przykład produkcyjny

```dotenv
OTTER_ENVIRONMENT=production
OTTER_DEBUG=false
OTTER_DATABASE_URL=sqlite+aiosqlite:////opt/otter-password-manager/backend/data/otter_password_manager.db
OTTER_LOG_LEVEL=INFO
OTTER_LOG_FORMAT=json
OTTER_JWT_SECRET=<unikalny-sekret-produkcji>
OTTER_ACCESS_TOKEN_EXPIRE_MINUTES=15
OTTER_REFRESH_TOKEN_EXPIRE_DAYS=30
OTTER_ENCRYPTION_KEY=<unikalny-klucz-produkcji>
OTTER_UVICORN_HOST=127.0.0.1
OTTER_UVICORN_PORT=8000
OTTER_UVICORN_RELOAD=false
```

W URL SQLite cztery ukośniki po `sqlite:` oznaczają bezwzględną ścieżkę Unix.

## Konfiguracja Unity

Adres API jest obecnie stałą w `ApplicationBootstrapper.cs`:

```csharp
private const string LocalApiUrl = "http://127.0.0.1:8000";
```

`127.0.0.1` w buildzie oznacza urządzenie użytkownika, nie VPS. Przed buildem
produkcyjnym zmień go na publiczny adres HTTPS. Docelowe rozwiązanie powinno mieć
profile środowiskowe, np. `ApiConfiguration` jako `ScriptableObject`.

## Walidacja konfiguracji

Niepoprawny lub zbyt krótki `OTTER_JWT_SECRET` zatrzyma start. `EncryptionService`
odrzuci klucz, który nie jest poprawnym Base64 albo po dekodowaniu nie ma 32 bajtów.
To celowe: aplikacja nie powinna wystartować z niebezpieczną konfiguracją.
