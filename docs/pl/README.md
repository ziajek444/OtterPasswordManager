# Otter Password Manager — dokumentacja

[English version](../en/README.md)

Otter Password Manager składa się z klienta Unity oraz niezależnego backendu REST.
Backend przechowuje dane w SQLite, uwierzytelnia użytkowników przez JWT i szyfruje
hasła sejfu za pomocą AES-256-GCM.

## Spis dokumentów

- [Architektura](architecture.md) — komponenty, warstwy, zależności i diagramy.
- [Backend](backend.md) — uruchamianie, struktura kodu, logowanie i testy.
- [Klient Unity](unity-client.md) — UI, klient REST i uruchamianie aplikacji.
- [REST API](api.md) — wszystkie endpointy, formaty danych i przykłady.
- [Baza danych](database.md) — SQLite, schemat, kopie zapasowe i odtwarzanie.
- [Bezpieczeństwo](security.md) — Argon2, JWT, AES-GCM i zarządzanie sekretami.
- [Konfiguracja](configuration.md) — wszystkie zmienne `.env`.
- [Wdrożenie](deployment.md) — przykładowe wdrożenie na VPS i diagnostyka.

## Szybki start

Backend, bez aktywowania skryptu PowerShell:

```powershell
cd "D:\Unity Projekty\OtterPasswordManager\backend"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m otter_password_manager
```

Po uruchomieniu dostępne są:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Następnie otwórz scenę Unity i naciśnij **Play**. Interfejs tworzy się automatycznie,
a lokalny klient łączy się z `http://127.0.0.1:8000`.

## Stan obecnej wersji

Zaimplementowano rejestrację, logowanie, JWT, CRUD sejfu, szyfrowanie wpisów,
migracje i prosty interfejs Unity. Refresh token jest zwracany przy logowaniu, ale
nie istnieje jeszcze endpoint jego wymiany na nowy access token.

> **Uwaga produkcyjna:** endpointy `/api/v1/users` nie mają kontroli ról i nie
> powinny być publicznie dostępne bez dodania autoryzacji administracyjnej.
