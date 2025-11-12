# KSeF Client for Odoo 18

Integration of Odoo 18 with the Polish National e-Invoicing System (KSeF). This module aims to send and receive structured e-invoices compliant with the official KSeF specification.

## Status

Early scaffold: module structure + authentication client (stub) + smoke tests + quality config.

## Project structure

```
__manifest__.py        # Odoo module manifest
models/                # Odoo model extensions (currently empty)
ksef_api_client/       # KSeF integration layers
   auth.py              # Authentication (stub token)
tests/                 # Smoke tests (Python)
.github/               # Issue/PR templates + Copilot instructions
pyproject.toml         # Ruff configuration
CONTRIBUTING.md        # Contribution guidelines
docker/odoo/Dockerfile # Multi-stage Dockerfile (base/dev/test/prod)
compose/               # Compose overlays per environment
requirements.txt       # Python dependencies (installed into venv)
config/*.conf          # Odoo config files (dev/test/prod)
```

## Multi-environment setup (Docker)

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system:
- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

You can use the provided Makefile to simplify commands. All examples below include both Makefile and raw docker compose forms.

### Dev environment (hot-reload)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mkieszek/ksef_client.git
   cd ksef_client
   ```

2. **Build (first run or after requirements change):**
    - Using Makefile (recommended):
       ```bash
       make dev-build
       ```
    - Or with docker compose overlays:
       ```bash
       docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.dev.yml build odoo
       ```

3. **Start the development environment (overlay compose):**
    - Using Makefile:
       ```bash
       make dev-up
       ```
    - Or with docker compose overlays:
       ```bash
       docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.dev.yml up -d --build
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
    - Using Makefile:
       ```bash
       make dev-down
       ```
    - Or with docker compose:
       ```bash
       docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.dev.yml down
       ```

6. **Useful dev helpers:**
    - Logs
       ```bash
       make dev-logs
       # or
       docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.dev.yml logs -f odoo
       ```
    - Odoo shell
       ```bash
       make dev-shell
       # or
       docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.dev.yml exec odoo odoo shell --config /etc/odoo/odoo.conf
       ```
    - Update/reload module in DB (after Python/XML changes)
       ```bash
       make update-module
       ```

### Test (CI-like) environment

Run ephemeral test container (installs module + runs tests + lint):
```bash
docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.test.yml up --abort-on-container-exit --build
```

Or simply run the tests and lint locally via Makefile:
```bash
make test
make lint
```

### Production build preview

Build production image only (no dev/test extras):
```bash
docker build --target=prod -t ksef_client:prod -f docker/odoo/Dockerfile .
```

Run production overlay locally (minimal runtime, mounts for filestore and config):
```bash
make prod-up
# or
docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.prod.yml up -d --build
```

Stop production overlay:
```bash
make prod-down
# or
docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.prod.yml down
```

### Running Tests and Linting (Dev container)

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

### Debugging in dev (VS Code attach)

The dev container starts Python with `debugpy` listening on port `5678` (see dev overlay). To attach from VS Code:

1. Install the “Python” extension in VS Code.
2. Add a launch configuration of type “Python: Attach using Process Id” or “Python: Remote Attach” targeting `localhost:5678`.
3. Set breakpoints in your module code under `ksef_client/` and attach; requests handled by Odoo will pause accordingly.

### Troubleshooting

**Port conflicts:**
If ports 8069 or 5432 are already in use on your system, change them in the dev overlay `compose/docker-compose.dev.yml`:

```yaml
ports:
  - "8070:8069"  # Change host port from 8069 to 8070
```

**Rebuild after dependency changes (dev):**
If you modify `requirements.txt` or `docker/odoo/Dockerfile`, rebuild the dev image:

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

## Alternative local (without Docker)

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

See `.github/copilot-instructions.md` for the Issue Contract, security rules, and Definition of Done used by Copilot-driven work.

## CI

GitHub Actions workflow `.github/workflows/ci.yml` runs on push/PR:
- Lint + tests using the test compose overlay
- Build the production image

You can replicate locally with:
```bash
make ci
```

## Security

Never commit certificates/keys. Key files are ignored by `.gitignore`. Use mocks and placeholder paths in tests.

In production overlay, provide secrets via Docker/host-level mounts or environment variables. Do not store sensitive data in the repository.

## Next steps

- Implement real signing and token exchange.
- Validate XML against KSeF schemas.
- Integrate with `account.move` models (export/import).

## FAQ (Docker)

- Change port 8069? Edit dev compose overlay (`compose/docker-compose.dev.yml`) ports section.
- Add new Python packages? Append to `requirements.txt` and rebuild: `docker compose build --no-cache odoo`.
- Where are logs? `docker compose logs -f odoo` or set `logfile` in the relevant config.
- How to run only production? Use prod overlay: `docker compose -f compose/docker-compose.base.yml -f compose/docker-compose.prod.yml up -d --build`.

## License

LGPL-3.0
