# Backend FastAPI

[English version](../en/backend.md)

## Wymagania

- Python 3.13,
- wirtualne środowisko `backend/.venv`,
- zależności z `backend/pyproject.toml`.

## Instalacja

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\alembic.exe upgrade head
```

Aktywowanie `.venv` nie jest wymagane. Jeśli PowerShell blokuje `Activate.ps1`,
używaj bezpośrednio plików wykonywalnych z `.venv\Scripts`.

## Uruchamianie

```powershell
.\.venv\Scripts\python.exe -m otter_password_manager
```

Uvicorn odczytuje host, port i tryb reload z `.env`. Zatrzymanie: `Ctrl+C`.
Restart procesu nie usuwa danych z SQLite.

## Struktura

```text
backend/
├── migrations/                 # środowisko i wersje Alembic
├── data/                       # lokalny plik SQLite
├── src/otter_password_manager/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   ├── main.py
│   └── __main__.py
├── tests/
├── .env                        # lokalne sekrety, ignorowane przez Git
├── .env.example                # szablon
├── alembic.ini
└── pyproject.toml
```

## Dependency injection

Projekt używa jawnego `ApplicationContainer`, bez zewnętrznego frameworka DI.
FastAPI pobiera kontener przez `app.state.container`, a zależności prezentacji
udostępniają konkretne serwisy. W testach porty można zastąpić atrapami.

## Logowanie

`OTTER_LOG_FORMAT=console` daje czytelne logi tekstowe. `json` emituje po jednym
obiekcie JSON na linię, co ułatwia integrację z systemem zbierania logów. Poziom
ustawia `OTTER_LOG_LEVEL`.

Nigdy nie należy logować:

- haseł logowania,
- haseł wpisów,
- access i refresh tokenów,
- klucza szyfrującego ani sekretu JWT.

## Testy i jakość

```powershell
.\.venv\Scripts\ruff.exe check src migrations tests
.\.venv\Scripts\pytest.exe -q
```

Testy jednostkowe obejmują m.in. rejestrację, logowanie, JWT, middleware,
szyfrowanie i reguły własności wpisów.

## Diagnostyka backendu

- `ModuleNotFoundError`: uruchom interpreter z `backend/.venv` i ponów instalację.
- `no such table`: wykonaj `alembic upgrade head` z katalogu `backend`.
- `Address already in use`: zmień `OTTER_UVICORN_PORT` lub zakończ stary proces.
- błąd walidacji ustawień: porównaj `.env` z `.env.example`.
- `InvalidTag` przy odszyfrowaniu: używany jest inny klucz niż podczas zapisu albo
  dane zostały zmodyfikowane.
