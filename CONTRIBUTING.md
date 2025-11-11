# CONTRIBUTING

Dziękujemy za wkład! Poniżej znajdziesz zasady współpracy, aby utrzymać jakość i bezpieczeństwo projektu.

## Flow pracy i gałęzie

- Nazewnictwo:
  - feature/<krótki-opis>
  - bugfix/<krótki-opis>
  - chore/<krótki-opis>
- Każda zmiana powinna mieć Issue z wypełnionym szablonem (Feature/Bug/Chore).
- Twórz małe, logiczne commity z czytelnymi opisami; odnoś link do Issue.

## Wymagane checki

- Ruff PASS (konfiguracja w `pyproject.toml`).
- Tests PASS (min. 1 happy path + 1 edge case). Testy integracyjne Odoo mogą być skipowane lokalnie, ale w PR musi być przynajmniej smoke test w `tests/`.
- Brak sekretów w repo (klucze, tokeny, certyfikaty).

## Styl i konwencje

- Zgodność z Odoo 18: nazwy modeli/pól, dekoratory `@api.*`, struktura modułu (`__manifest__.py`, `models/`, `views/`, itp.).
- Importy: standard → third-party → local (weryfikowane przez Ruff/isort).
- Docstringi dla publicznych funkcji/metod (parametry, zwrot, wyjątki) – krótkie i konkretne.

## Bezpieczeństwo

- Nie commituj plików .key/.pem/.p12/.crt/.cer i podobnych – dodano do `.gitignore`.
- Używaj sekretów środowiskowych (lokalnie `.env`, w CI – GitHub Secrets). W testach używaj mocków.
- Nie loguj danych wrażliwych; maskuj identyfikatory.

## Testy

- Jednostkowe: logika `ksef_api_client/` – mocno mockuj I/O i kryptografię.
- Integracyjne: rozszerzenia modeli Odoo – użyj frameworka Odoo, dane demo.
- Domyślnie unikamy wywołań sieciowych; sandbox KSeF tylko w testach oznaczonych i wyłączonych domyślnie.

## PR i review

- Dołącz opis zmian, kroki testów oraz checklistę Quality Gates (w szablonie PR).
- Reviewer sprawdza bezpieczeństwo, zgodność z Odoo, testy i dokumentację.

Dziękujemy za stosowanie się do zasad – to utrzymuje projekt szybkim i bezpiecznym.
