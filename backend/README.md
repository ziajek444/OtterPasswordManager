# Otter Password Manager API

Pełna dokumentacja rozwiązania znajduje się w [`../docs/README.md`](../docs/README.md).

Szkielet backendu w Pythonie 3.13, oparty na FastAPI, SQLAlchemy 2 i SQLite.

## Uruchomienie

```powershell
cd backend
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
alembic upgrade head
python -m otter_password_manager
* alternatywnie:
cd backend/
.\.venv\Scripts\python.exe -m otter_password_manager
```

Konfiguracja jest odczytywana z pliku `.env` oraz zmiennych środowiskowych z
prefiksem `OTTER_`. Zmienne środowiskowe mają pierwszeństwo przed plikiem.

## Migracje

```powershell
alembic revision --autogenerate -m "opis zmiany"
alembic upgrade head
alembic downgrade -1
```

Przed wygenerowaniem migracji wszystkie modele SQLAlchemy muszą zostać
zaimportowane w `infrastructure/database/models/__init__.py`.

## Users API

CRUD użytkowników jest dostępny pod adresem `/api/v1/users`:

- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

API przyjmuje pole `password`, lecz nigdy go nie zapisuje ani nie zwraca wprost.
W bazie przechowywany jest wyłącznie hash Argon2 z losową solą.

Rejestracja jest dostępna jako `POST /register`. Login musi być unikalny, a hasło
musi zawierać co najmniej 12 znaków.

Logowanie jest dostępne jako `POST /login` i zwraca tokeny `access_token` oraz
`refresh_token`. Trasy `/api/v1/*` wymagają nagłówka
`Authorization: Bearer <access_token>`. Token refresh nie służy do autoryzacji żądań API.

Hasła wpisów sejfu szyfruje `EncryptionService` przy użyciu AES-256-GCM. Klucz jest
odczytywany z `OTTER_ENCRYPTION_KEY` jako 32 bajty zakodowane URL-safe Base64 i nie
jest zapisywany w bazie. Nowy klucz można wygenerować poleceniem:

```powershell
py -3.13 -c "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
```

CRUD sejfu jest dostępny pod `/passwords` i wymaga access tokenu. Właściciel jest
ustalany wyłącznie z JWT; API nie przyjmuje `owner_id`. Hasło jest szyfrowane przed
zapisem i odszyfrowywane tylko w odpowiedzi dla właściciela wpisu.
