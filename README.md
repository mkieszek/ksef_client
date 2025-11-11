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

## Jak uruchomić lint

```bash
pip install ruff
ruff check .
```

## Jak uruchomić testy (smoke)

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
