# Architektura rozwiązania

[English version](../en/architecture.md)

## Widok systemowy

```mermaid
flowchart LR
    U[Użytkownik] --> UI[Unity UI<br/>PasswordManagerController]
    UI --> AC[IApiClient / ApiClient]
    AC --> HT[UnityHttpTransport]
    HT -->|HTTPS + JSON + Bearer JWT| RP[Reverse proxy<br/>Caddy lub Nginx]
    RP --> API[FastAPI / Uvicorn]
    API --> MW[JWT middleware]
    MW --> UC[Serwisy aplikacyjne]
    UC --> ENC[EncryptionService<br/>AES-256-GCM]
    UC --> REP[Repozytoria SQLAlchemy]
    REP --> DB[(SQLite)]
    API --> JWT[JwtTokenService]
    API --> ARGON[Argon2PasswordHasher]
    ENC -. klucz z .env .-> ENV[Sekrety VPS]
    JWT -. sekret z .env .-> ENV
```

Unity i backend są osobnymi procesami. Unity nigdy nie odwołuje się bezpośrednio
do SQLite ani kodu Pythona. Jedyną granicą komunikacji jest REST API.

## Backend — Clean Architecture

```mermaid
flowchart TB
    P[Presentation<br/>FastAPI, schematy, middleware] --> A[Application<br/>serwisy, DTO, porty]
    I[Infrastructure<br/>SQLAlchemy, JWT, Argon2, AES-GCM] --> A
    A --> D[Domain<br/>encje i interfejsy repozytoriów]
    I --> D
```

Zasada zależności: kod wewnętrzny nie zna frameworków zewnętrznych.

### Domain

- `User` — użytkownik sejfu.
- `PasswordEntry` — wpis zawierający zaszyfrowane hasło.
- `UserRepository`, `PasswordEntryRepository` — kontrakty trwałości danych.

### Application

- `UserService` — CRUD użytkowników i reguły rejestracji.
- `AuthenticationService` — weryfikacja danych logowania i wydawanie tokenów.
- `PasswordEntryService` — CRUD sejfu, kontrola właściciela i użycie szyfrowania.
- porty `UnitOfWork`, `PasswordHasher`, `TokenService`, `EncryptionPort`.
- DTO niezależne od FastAPI i SQLAlchemy.

### Infrastructure

- modele i repozytoria SQLAlchemy,
- `SqlAlchemyUnitOfWork`,
- `Argon2PasswordHasher`,
- `JwtTokenService`,
- `EncryptionService`,
- konfiguracja, sesje bazy i logowanie.

### Presentation

- routery FastAPI,
- schematy Pydantic,
- middleware JWT,
- dependency injection i mapowanie wyjątków na odpowiedzi HTTP.

### Composition root

`ApplicationContainer` tworzy silnik bazy, fabrykę sesji, implementacje portów i
serwisy. `main.py` składa aplikację FastAPI i zarządza czasem życia zasobów.

## Unity — podział odpowiedzialności

```mermaid
flowchart LR
    V[Presentation<br/>UI i controller] --> IA[Application<br/>IApiClient + modele]
    C[Composition<br/>bootstrapper] --> V
    C --> INF[Infrastructure<br/>ApiClient, HTTP, token store]
    INF --> IA
```

- `PasswordManagerController` buduje widoki i obsługuje zdarzenia użytkownika.
- `IApiClient` jest kontraktem używanym przez UI.
- `ApiClient` mapuje operacje aplikacji na endpointy.
- `UnityHttpTransport` odpowiada wyłącznie za HTTP i JSON.
- `ITokenStore` oddziela sposób przechowywania tokenów.
- `ApplicationBootstrapper` tworzy i łączy obiekty po załadowaniu sceny.

## Scenariusz: zapis hasła

```mermaid
sequenceDiagram
    actor User as Użytkownik
    participant UI as Unity UI
    participant Client as ApiClient
    participant HTTP as UnityHttpTransport
    participant MW as JWT middleware
    participant API as FastAPI / PasswordEntryService
    participant AES as EncryptionService
    participant Repo as SQLAlchemy repository
    participant DB as SQLite

    User->>UI: Wypełnia formularz i wybiera Zapisz
    UI->>Client: CreatePasswordAsync(dane)
    Client->>HTTP: POST /passwords + access token
    HTTP->>MW: HTTPS, JSON, Bearer JWT
    MW->>MW: Weryfikacja podpisu, exp i type=access
    MW->>API: owner_id z JWT + dane wpisu
    API->>AES: encrypt(hasło jawne)
    AES-->>API: v1.nonce.ciphertext+tag
    API->>Repo: add(owner_id, encrypted_password, ...)
    Repo->>DB: INSERT
    DB-->>Repo: zapisany rekord
    Repo-->>API: PasswordEntry
    API->>AES: decrypt(encrypted_password)
    API-->>HTTP: 201 + JSON właściciela
    HTTP-->>Client: PasswordEntry
    Client-->>UI: wynik
    UI-->>User: Odświeżona lista
```

Hasło jawne istnieje chwilowo w pamięci klienta, w żądaniu HTTPS i w pamięci
backendu. W SQLite zapisywana jest wyłącznie koperta AES-GCM.
