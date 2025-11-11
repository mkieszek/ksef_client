# Instrukcje dla GitHub Copilot - Moduł KSeF dla Odoo 18

## Cel Repozytorium

To repozytorium zawiera kod modułu Odoo 18, który integruje system Odoo z polskim Krajowym Systemem e-Faktur (KSeF). Głównym celem jest umożliwienie wysyłania i odbierania faktur ustrukturyzowanych (e-Faktur) bezpośrednio z Odoo.

## Główne założenia projektu

- **Zgodność z Odoo:** Kod musi być zgodny ze standardami programistycznymi Odoo 18, w tym strukturą modułów, nazewnictwem modeli, pól i metod, a także konwencjami dotyczącymi widoków i logiki biznesowej.
- **Zgodność z KSeF:** Implementacja musi być w pełni zgodna z aktualną dokumentacją techniczną i schematami Krajowego Systemu e-Faktur.
- **Bezpieczeństwo:** Kod musi być bezpieczny, ze szczególnym uwzględnieniem zarządzania certyfikatami, kluczami prywatnymi i tokenami autoryzacyjnymi. Należy unikać przechowywania wrażliwych danych w kodzie źródłowym.
- **Wydajność:** Rozwiązanie powinno być wydajne i zoptymalizowane pod kątem obsługi dużej liczby faktur, aby nie spowalniać działania systemu Odoo.
- **Łatwość utrzymania:** Kod powinien być czytelny, dobrze udokumentowany i łatwy w utrzymaniu oraz dalszym rozwoju.

## Struktura projektu

Projekt jest standardowym modułem Odoo 18. Przestrzegaj następującej struktury katalogów:

- `controllers/`: Kontrolery webowe, jeśli będą potrzebne.
- `models/`: Modele danych Odoo (pliki Python).
- `views/`: Widoki Odoo (pliki XML).
- `wizards/`: Kreatory (pliki XML i Python).
- `security/`: Reguły bezpieczeństwa (pliki `ir.model.access.csv` i XML).
- `static/`: Pliki statyczne (CSS, JS, obrazy).
- `data/`: Dane początkowe (pliki XML).
- `demo/`: Dane demonstracyjne (pliki XML).
- `tests/`: Testy jednostkowe i integracyjne.
- `i18n/`: Pliki z tłumaczeniami (`.po`).

## Klient KSeF

Logika komunikacji z API KSeF powinna być wyizolowana w osobnej bibliotece. Preferowane jest umieszczenie jej w dedykowanym katalogu, np. `ksef_api_client/`.

### Uwierzytelnianie

- Uwierzytelnianie do KSeF musi być realizowane za pomocą certyfikatu i klucza prywatnego.
- Implementacja powinna obsługiwać wczytywanie certyfikatu i klucza prywatnego z bezpiecznej lokalizacji (np. załącznik w Odoo, plik na serwerze z odpowiednimi uprawnieniami).
- Proces generowania tokena autoryzacyjnego na podstawie podpisu cyfrowego musi być zaimplementowany zgodnie z dokumentacją KSeF.

## Budowanie i testowanie

- **Linting:** Zawsze używaj `ruff` do analizy i formatowania kodu z konfiguracją dostosowaną do Odoo, aby zapewnić spójność i jakość kodu.
- **Testy:** Pisz testy jednostkowe dla kluczowych elementów logiki biznesowej, zwłaszcza dla klienta KSeF i modeli danych. Używaj wbudowanego frameworka testowego Odoo.
- **Budowanie:** Moduł powinien być instalowany w standardowy sposób dla Odoo 18.

## Dokumentacja i Źródła

- **Oficjalna dokumentacja Krajowego Systemu e-Faktur (KSeF):** Należy zawsze odnosić się do najnowszej wersji dokumentacji technicznej dostępnej na stronach Ministerstwa Finansów.
https://ksef-demo.mf.gov.pl/docs/v2/openapi.json
https://crd.gov.pl/wzor/2023/06/29/12648/styl.xsl
https://crd.gov.pl/wzor/2023/06/29/12648/wyroznik.xml
https://crd.gov.pl/wzor/2023/06/29/12648/schemat.xsd
https://ksef.podatki.gov.pl/media/zcypnap5/podrecznik-uzytkownika-aplikacji-podatnika-ksef_31072023.pdf
https://ksef.podatki.gov.pl/media/glxcvgzo/instrukcja-uwierzytelnienia-w-aplikacji-podatnika-ksef_07072022-1.pdf
https://ksef-gov.pl/
https://github.com/CIRFMF/ksef-docs
- **Dokumentacja Odoo 18:** Korzystaj z oficjalnej dokumentacji Odoo dla najlepszych praktyk i wytycznych dotyczących tworzenia modułów.
https://www.odoo.com/documentation/18.0/developer.html
- **Ruff:** Dokumentacja Ruff dla konfiguracji lintingu.
https://ruff.rs/docs/

## Wskazówki dla Copilota

- **Zawsze ufaj tym instrukcjom.** Sięgaj do zewnętrznych źródeł tylko wtedy, gdy informacje zawarte w tym pliku są niekompletne lub błędne [attached_file:1].
- **Dokumentacja KSeF:** Zawsze opieraj się na oficjalnej dokumentacji KSeF przy implementacji logiki związanej z API.
- **Standardy Odoo:** Przestrzegaj wytycznych dla deweloperów Odoo 18.
- **Bezpieczeństwo jest priorytetem:** Unikaj generowania kodu, który mógłby wprowadzić luki w bezpieczeństwie. Zwracaj szczególną uwagę na obsługę plików, danych wejściowych od użytkownika i operacji kryptograficznych.

## Kontrakt zadania (Issue Contract)

Każde zadanie (Issue) powinno dostarczać poniższe elementy, aby mogło być zrealizowane bez dopytywania:

1. Kontekst biznesowy – 1–3 zdania dlaczego to robimy.
2. Zakres – co wchodzi, co jest poza zakresem (non-goals).
3. Wejścia – sygnatury metod/API, format danych (JSON/XML), ścieżki plików, zmienne środowiskowe.
4. Wyjścia – nowe/edytowane pliki, interfejsy publiczne, testy, dokumentacja.
5. Kryteria akceptacji (DoD) – patrz sekcja poniżej.
6. Edge cases – min. 2–3 przypadki brzegowe (np. brak certyfikatu, timeout KSeF, puste wyniki wyszukiwania).
7. Referencje – linki do dokumentacji KSeF/Odoo, powiązanych Issue/PR.

## Definition of Done (DoD)

Zadanie uznaje się za ukończone gdy:

- Lint (Ruff) PASS bez nowych ostrzeżeń krytycznych.
- Testy PASS: co najmniej 1 happy path + 1 edge case (jeśli logika).
- Brak wycieków bezpieczeństwa (żadnych kluczy, certyfikatów, tokenów w repo).
- Kod zgodny ze stylami Odoo 18 (nazwa modeli, pól, dekoratory api, struktura modułu).
- Publiczne API udokumentowane w docstringach (krótko: parametry, zwroty, wyjątki).
- Logi nie zawierają danych wrażliwych.
- Dodane lub zaktualizowane tłumaczenia (i18n) dla nowych stringów widocznych dla użytkownika.
- README lub odpowiednia sekcja zaktualizowana, jeśli zmiana wpływa na instalację/uruchamianie.

## Polityka bezpieczeństwa

1. Certyfikaty/klucze prywatne: nigdy nie commituj. Używaj zmiennych środowiskowych lub załączników Odoo przechowywanych poza repo.
2. Tokeny/sekrety: mockuj w testach, przechowuj w bezpiecznych sekretach (np. GitHub Secrets) – nie w plikach .py.
3. Logowanie: maskuj fragmenty danych (np. tylko fingerprint certyfikatu). Nie loguj pełnych payloadów z danymi osobowymi.
4. Walidacja wejść: sanitacja danych użytkownika – szczególnie nazwy plików, identyfikatory, parametry filtrowania.
5. XML/Schema: waliduj dokumenty e-Faktur względem XSD przed wysyłką. Błędy walidacji ➝ komunikuj jasno (UserError w Odoo).

## Logowanie i obsługa błędów

- Używaj `logging.getLogger(__name__)`.
- Poziomy: DEBUG (szczegóły techniczne), INFO (zdarzenia biznesowe), WARNING (niekrytyczne problemy), ERROR (błąd funkcjonalny), CRITICAL (awaria).
- Nie przechowuj w wyjątkach pełnych danych wrażliwych (tokeny, klucze).
- W warstwie Odoo preferuj `UserError` dla błędów biznesowych i `ValidationError` dla błędów walidacji.

## i18n

- Wszystkie nowe komunikaty użytkownika muszą trafić do domeny tłumaczeń Odoo (użycie `_()`).
- Nie tłumaczymy technicznych logów DEBUG.

## Testowanie

Typy testów:
- Jednostkowe (logika klienta KSeF) – mockowanie HTTP i kryptografii.
- Integracyjne (Odoo models) – użycie frameworka testowego Odoo, danych demo w razie potrzeby.

Zasady:
- Unikaj realnych wywołań produkcyjnego KSeF w testach. Sandbox tylko w dedykowanych testach oznaczonych (skip domyślnie).
- Mocki muszą sprawdzać kluczowe ścieżki: sukces, błąd walidacji, timeout, nieautoryzowany.
- Minimalny coverage dla nowej krytycznej logiki: 2 ścieżki (happy + error).

## Kiedy zadawać pytania zamiast działać

Zapytaj jeśli:
1. Brak jednoznacznego źródła certyfikatu/klucza w opisie zadania.
2. Sprzeczne wymagania wydajnościowe vs. bezpieczeństwo.
3. Zadanie rozszerza publiczne API bez zdefiniowanych wersji kompatybilności.
4. Brak specyfikacji struktury danych, a wpływa ona na wiele modeli.

W innych przypadkach: przyjmij rozsądne domniemania (np. standardowy endpoint sandbox KSeF, brak dodatkowych zależności) i kontynuuj.

## Konwencje implementacyjne

- Nazwy plików: snake_case, brak wielkich liter.
- Nazwy klas modeli: `res.company`, `account.move` rozszerzane przez dziedziczenie (`_inherit`).
- Klient KSeF: moduł `ksef_api_client` z warstwami: auth, transport, serialization, validation.
- Importy: grupowanie (standard lib, third party, lokalne) – wymuszane przez Ruff/isort.
- Funkcje publiczne: docstring (krótki opis, parametry, zwrot, wyjątki).

## Edge cases do rozważenia (lista bazowa)

1. Brak pliku certyfikatu / nieczytelny (permissions / format).
2. Niezgodny klucz prywatny z certyfikatem.
3. Timeout po stronie KSeF.
4. Błąd walidacji XSD (element brakujący / zły typ).
5. Pusta odpowiedź API lub status 202 (opóźnione przetwarzanie).

## Struktura katalogów – rozszerzenia

Dodajemy katalog `ksef_api_client/`:
```
ksef_api_client/
  __init__.py
  auth.py          # Uwierzytelnianie, podpisy, tokeny
  transport.py     # Warstwa komunikacji HTTP (requests / aiohttp w przyszłości)
  serializers.py   # Konwersje danych (JSON/XML)
  validators.py    # Walidacja XSD, reguły biznesowe
```

## Quality Gates

Przed oznaczeniem zadania jako DONE:
1. Ruff PASS.
2. Testy PASS.
3. Brak zmian w plikach zastrzeżonych (.cert/.key) w repo.
4. Brak naruszenia konwencji struktury modułu Odoo.
5. Brak TODO bez uzasadnienia – jeśli zostawiasz, dodaj tag `# TODO(reason, issue-link)`.

## Przykład opisu metody (docstring wzorzec)

```python
def generate_auth_token(self, challenge: str) -> str:
	"""Generate KSeF auth token from challenge.

	Parametry:
		challenge: Losowy ciąg otrzymany z endpointu KSeF.

	Zwraca:
		Auth token (string) ważny czasowo.

	Wyjątki:
		ValueError: jeśli challenge jest pusty.
		KsefAuthError: jeśli podpis nie może być wygenerowany.
	"""
```

## Przyszłe rozszerzenia (roadmap skrócona)

- Asynchroniczna komunikacja (aiohttp) dla masowej wysyłki.
- Cache tokenów z rotacją i odświeżaniem.
- Walidacja semantyczna numeracji faktur.
- Monitorowanie (metryki czasu odpowiedzi, liczba błędów).

---
Aktualizuj ten plik gdy pojawią się nowe zasady lub procesy – jest źródłem prawdy dla automatycznych zadań.
