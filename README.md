# KSeF Client for Odoo 18

Integracja Odoo 18 z Krajowym Systemem e-Faktur (KSeF). Moduł umożliwi wysyłanie i odbiór ustrukturyzowanych e-Faktur zgodnie z oficjalną specyfikacją KSeF.

## Status

Wczesny scaffold: struktura modułu + klient uwierzytelniania (stub) + testy smoke + konfiguracja jakości.

## Struktura

```
__manifest__.py        # Metadane modułu Odoo
models/                # Rozszerzenia modeli Odoo (puste)
ksef_api_client/       # Warstwa integracji z KSeF
    auth.py              # Uwierzytelnianie (stub token)
tests/                 # Testy smoke (Python)
.github/               # Szablony Issue/PR + instrukcje Copilot
pyproject.toml         # Konfiguracja Ruff
CONTRIBUTING.md        # Zasady współpracy
```

## Development Setup (Docker)

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system:
- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mkieszek/ksef_client.git
   cd ksef_client
   ```

2. **Start the development environment:**
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start PostgreSQL 16 database on port 5432
   - Start Odoo 18.0 on port 8069
   - Mount the `ksef_client` module to `/mnt/extra-addons/ksef_client`

3. **Access Odoo:**
   - Open your browser and navigate to `http://localhost:8069`
   - Create a new database using the web interface
   - Install the `ksef_client` module from the Apps menu

4. **Stop the environment:**
   ```bash
   docker-compose down
   ```

### Running Tests and Linting

Execute commands inside the Odoo container:

```bash
# Run Ruff linter
docker-compose exec odoo ruff check /mnt/extra-addons/ksef_client

# Run Ruff formatter
docker-compose exec odoo ruff format /mnt/extra-addons/ksef_client

# Access Odoo shell
docker-compose exec odoo odoo shell --config /etc/odoo/odoo.conf
```

### Troubleshooting

**Port conflicts:**
If ports 8069 or 5432 are already in use on your system, you can change them in `docker-compose.yml`:

```yaml
ports:
  - "8070:8069"  # Change host port from 8069 to 8070
```

**Rebuild after dependency changes:**
If you modify `requirements.txt`, rebuild the Odoo image:

```bash
docker-compose build odoo
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f odoo
```

## Alternative Setup (Local)

### Jak uruchomić lint

```bash
pip install ruff
ruff check .
```

### Jak uruchomić testy (smoke)

```bash
python -m pytest -q
```

## Praca z Issues

Używaj szablonów: Feature, Bug, Chore. Każde zadanie zawiera kontekst, zakres, wejścia, wyjścia, DoD, edge cases oraz referencje.

## Bezpieczeństwo

Nigdy nie commituj certyfikatów/kluczy. Pliki kluczy są ignorowane przez `.gitignore`. W testach używaj mocków i ścieżek placeholder.

## Następne kroki

- Implementacja realnego podpisu i wymiany tokena.
- Walidacja XML względem schematów KSeF.
- Integracja z modelami `account.move` (export/import). 

## Licencja

LGPL-3.0
