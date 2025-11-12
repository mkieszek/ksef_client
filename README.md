# KSeF Client for Odoo 18

Integration of Odoo 18 with the Polish National e-Invoicing System (KSeF). This module aims to send and receive structured e-invoices compliant with the official KSeF specification.

## Status

Early scaffold: module structure + authentication client (stub) + smoke tests + quality config.

## Project structure

```
__manifest__.py        # Metadane modułu Odoo
models/                # Rozszerzenia modeli Odoo (puste)
ksef_api_client/       # Warstwa integracji z KSeF
    auth.py              # Uwierzytelnianie (stub token)
tests/                 # Testy smoke (Python)
.github/               # Szablony Issue/PR + instrukcje Copilot
pyproject.toml         # Konfiguracja Ruff
CONTRIBUTING.md        # Zasady współpracy
docker-compose.yml     # Środowisko deweloperskie (PostgreSQL + Odoo)
docker/odoo/Dockerfile # Obraz Odoo 18 z venv + pip
requirements.txt       # Dodatkowe zależności Pythona (instalowane do venv)
config/odoo.conf       # Konfiguracja Odoo (addons_path, DB, logi)
```

## Development setup (Docker)

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system:
- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

### Quick start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mkieszek/ksef_client.git
   cd ksef_client
   ```

2. **Build (first run or after requirements change):**
   ```bash
   docker compose build --no-cache odoo
   ```

3. **Start the development environment:**
   ```bash
   docker compose up -d
   ```

   This will:
   - Start PostgreSQL 16 database on port 5432
   - Start Odoo 18.0 on port 8069
   - Mount the `ksef_client` module to `/mnt/extra-addons/ksef_client`

4. **Access Odoo:**
   - Open your browser and navigate to `http://localhost:8069`
   - Create a new database using the web interface
   - Install the `ksef_client` module from the Apps menu

5. **Stop the environment:**
   ```bash
   docker compose down
   ```

### Running Tests and Linting

Execute commands inside the Odoo container:

```bash
# Run Ruff linter
docker compose exec odoo ruff check /mnt/extra-addons/ksef_client

# Run Ruff formatter
docker compose exec odoo ruff format /mnt/extra-addons/ksef_client

# Access Odoo shell
docker compose exec odoo odoo shell --config /etc/odoo/odoo.conf
```

Notes:
- The Odoo image uses a dedicated Python virtualenv at `/opt/odoo-venv`.
- Packages from `requirements.txt` are installed into that venv during image build.
- At runtime, Odoo (system Python) can import venv packages via a `.pth` link; no action needed.
- If you temporarily need a package for debugging (not persisted), you can run:
   ```bash
   docker compose exec odoo pip install <package>
   ```
   but remember this won’t persist across rebuilds; add it to `requirements.txt` for permanence.

### Troubleshooting

**Port conflicts:**
If ports 8069 or 5432 are already in use on your system, you can change them in `docker-compose.yml`:

```yaml
ports:
  - "8070:8069"  # Change host port from 8069 to 8070
```

**Rebuild after dependency changes:**
If you modify `requirements.txt` or `docker/odoo/Dockerfile`, rebuild the Odoo image:

```bash
docker compose build --no-cache odoo
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f odoo
```

**Addons path and mounts:**
- The repository is mounted read-only at `/mnt/extra-addons/ksef_client`.
- `addons_path` in `config/odoo.conf` includes `/mnt/extra-addons`, so Odoo detects the `ksef_client` module.

**Clean up volumes (reset DB):**
```bash
docker compose down -v
```

## Alternative setup (local)

### How to run lint

```bash
pip install ruff
ruff check .
```

### How to run tests (smoke)

```bash
python -m pytest -q
```

## Working with Issues

Use the provided templates: Feature, Bug, Chore. Each task should include context, scope, inputs, outputs, DoD, edge cases, and references.

## Security

Never commit certificates/keys. Key files are ignored by `.gitignore`. Use mocks and placeholder paths in tests.

## Next steps

- Implement real signing and token exchange.
- Validate XML against KSeF schemas.
- Integrate with `account.move` models (export/import).

## FAQ (Docker)

- Czy mogę zmienić port 8069? Tak – edytuj `docker-compose.yml` (np. `"8070:8069"`).
- Czy mogę dodać nowe paczki Pythona? Dodaj do `requirements.txt` i przebuduj obraz (`docker compose build --no-cache odoo`).
- Gdzie są logi? Użyj `docker compose logs -f odoo` lub ustaw własny `logfile` w `config/odoo.conf`.

## License

LGPL-3.0
