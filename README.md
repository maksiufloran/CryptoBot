# cryptoBot 🤖📈

Automatyczny bot tradingowy oparty na API giełdy **Binance**, realizujący strategię podążania za trendem oraz analizy dynamiki rynku przy użyciu wskaźników analizy technicznej (**EMA** oraz **RSI**).

> ⚠️ **Status projektu: Wczesna faza deweloperska (Work in Progress / Proof of Concept)**
>
> Kod znajduje się obecnie na etapie prototypowania i weryfikacji założeń logicznych. Nie jest gotowy do handlu rzeczywistymi środkami bez wcześniejszego audytu, testów stabilności i implementacji mechanizmów bezpieczeństwa.

## 🎯 Zamysł i cel projektu

Głównym założeniem projektu jest stworzenie autonomicznego bota handlowego, który:

1. **Analizuje rynek w czasie rzeczywistym** – pobiera dane świecowe (interwał 1m/krótkoterminowy) dla wybranych par kryptowalutowych (np. `XRP/USDC`, `TURBO/USDC`, `SOL/USDC`).

2. **Generuje sygnały transakcyjne** – łączy przecięcia średnich kroczących (EMA 9/21) z weryfikacją poziomów wykupienia/wyprzedania na oscylatorze RSI (14).

3. **Zarządza alokacją portfela** – rozdziela dostępny kapitał (np. stabilnego coina USDC) według określonych wag procentowych dla poszczególnych aktywów.

4. **Zapewnia kontrolę ryzyka** – implementuje wstępne założenia dla zleceń typu Stop-Loss w celu minimalizacji strat.

## 📍 Na jakim etapie jest projekt? (Stan obecny)

Projekt znajduje się obecnie w fazie **prototypowania logiki i paper tradingu**:

* \[x\] **Integracja z Binance API:** Nawiązanie autoryzowanego połączenia przez bibliotekę `python-binance` z obsługą zmiennych środowiskowych (`.env`).

* \[x\] **Silnik wskaźników:** Zaimplementowane obliczenia szybkiej EMA (9), wolnej EMA (21) oraz RSI (14) na ramkach danych `pandas`.

* \[x\] **Zlecenia testowe:** Opracowanie modułu zleceń rynkowych oraz zleceń symulowanych (`testBuy`, `testSell` z API Binance).

* \[x\] **Pętla symulacyjna (`tester.py`):** Działający skrypt weryfikujący logikę w czasie rzeczywistym, wykonujący zlecenia testowe i zapisujący przebiegi do plików tekstowych.

* \[ \] **Handel na żywo (`trader.py`):** Kod egzekucji rzeczywistych transakcji jest obecnie przygotowany, lecz celowo zakomentowany do czasu pełnej walidacji strategii.

* \[ \] **Obsługa filtrów Binance:** Wymagana implementacja walidacji precyzji kroku (`LOT_SIZE`, `PRICE_FILTER`, `MIN_NOTIONAL`), aby zapobiec odrzucaniu zleceń przez giełdę.

* \[ \] **Synchronizacja salda portfela:** Metoda pobierania wolnych środków wymaga odkomentowania i dopracowania dynamicznego odczytu wolumenów.

## 🧠 Strategia handlowa

Bot podejmuje decyzje w oparciu o zestaw reguł łączących dwa filary:

### 1. Warunek wejścia (Sygnał KUPNA – `should_buy`)

Transakcja kupna jest inicjowana, gdy spełnione są jednocześnie 3 warunki:

* **Złoty krzyż EMA:** Szybka średnia $EMA_9$ przecina wolną średnią $EMA_{21}$ od dołu w górę.

* **Wybicie z wyprzedania RSI:** Wskaźnik RSI spadł wcześniej poniżej poziomu wyprzedania ($RSI < 30$), po czym zaczął rosnąć ponad tę wartość.

* **Potwierdzenie trendu:** Bieżąca cena zamknięcia świecy znajduje się powyżej wolnej średniej $EMA_{21}$.

### 2. Warunek wyjścia (Sygnał SPRZEDAŻY – `should_sell`)

Pozycja jest zamykana, gdy:

* **Śmiertelny krzyż EMA:** Szybka średnia $EMA_9$ przecina wolną $EMA_{21}$ od góry w dół.

* **Spadek z wykupienia RSI:** Wskaźnik RSI przekroczył poziom wykupienia ($RSI > 70$), a następnie zaczął spadać.

* **Potwierdzenie osłabienia:** Bieżąca cena zamknięcia spada poniżej wolnej średniej $EMA_{21}$.

### 3. Zabezpieczenie kapitału (Stop Loss)

Klasa egzekucyjna zawiera prototyp mechanizmu Stop-Loss, który kalkuluje procentowy spadek ceny względem ceny zakupu (domyślnie 3%) i wymusza zlecenie rynkowe sprzedaży w razie przekroczenia tego progu.

## 📂 Struktura repozytorium

```
cryptoBot/
├── logs/                      # Logi zdarzeń, transakcji testowych i błędów API
│   ├── calls_log.txt          # Historia zleceń rzeczywistych i stop loss
│   ├── test.log               # Historia zleceń testowych
│   ├── tester.txt             # Podsumowanie kolejnych iteracji testera
│   ├── tester_negative.txt    # Logi odrzuconych akcji i błędów BinanceAPIException
│   ├── tester_positive.txt    # Logi poprawnych sygnałów i podjętych akcji
│   └── trader_log.txt         # Logi egzekucyjne tradera
├── .env                       # Klucze API (plik prywatny, ignorowany w git)
├── .gitignore
├── binance_client.py          # Konfiguracja i inicjalizacja klienta Binance
├── call.py                    # Klasa Call: egzekucja zleceń (buy, sell, testBuy, stopLoss)
├── fetcher.py                 # Klasa MyFetcher: pobieranie tickerów, cen i salda
├── indicator.py               # Klasa Indicator: obliczenia EMA/RSI i logika sygnałów
├── tester.py                  # Pętla testowa (paper trading / symulacja live)
└── trader.py                  # Główna pętla handlowa na żywo (WIP)

```

## 🛠️ Instalacja i konfiguracja

### 1. Wymagania wstępne

* Python 3.10 lub nowszy

* Aktywne konto na giełdzie Binance z wygenerowanymi kluczami API (na etapie testów wystarczą uprawnienia `Read` i `Enable Spot & Margin Trading` w trybie testowym).

### 2. Klonowanie i środowisko wirtualne

```
# Klonowanie repozytorium
git clone <URL_TWOJEGO_REPOZYTORIUM>
cd cryptoBot

# Tworzenie i aktywacja środowiska wirtualnego
python -m venv .venv

# Windows (PowerShell / CMD):
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate

```

### 3. Instalacja zależności

```
pip install python-binance pandas python-dotenv

```

### 4. Konfiguracja zmiennych środowiskowych

Utwórz w głównym katalogu plik `.env` i uzupełnij go własnymi danymi dostępowymi:

```
BINANCE_API_KEY="twój_api_key"
BINANCE_API_SECRET="twój_api_secret"

```

> **Ważne:** Nigdy nie commituj pliku `.env` do publicznych repozytoriów! Upewnij się, że znajduje się w `.gitignore`.

## 🚀 Uruchomienie

### Uruchomienie trybu testowego (zalecane)

Skrypt pobiera dane rynkowe w 5-sekundowych interwałach, weryfikuje warunki i symuluje zlecenia za pośrednictwem endpointu `create_test_order`:

```
python tester.py

```

Wszystkie wyniki, błędy oraz sygnały będą na bieżąco dopisywane do katalogu `logs/`.

## 🗺️ Roadmapa (Kolejne kroki)

1. **Formatowanie wielkości zleceń (Lot Size & Precision):**

   * Odczyt reguł `exchange_info` dla każdej pary (krok ilości, minimalna wartość zlecenia).

2. **Usprawnienie pobierania danych:**

   * Przejście z odpytywania REST API (`get_klines`) na strumienie **WebSocket** (`BinanceSocketManager`) w celu redukcji opóźnień i limitów zapytań (rate limits).

3. **Moduł Backtestingu:**

   * Możliwość przetestowania zestawu parametrów EMA/RSI na danych historycznych przed uruchomieniem pętli na żywo.

4. **Baza danych zamiast plików `.txt`:**

   * Zastąpienie logowania plikowego bazą SQLite w celu łatwiejszej analizy zysków/strat (P&L).

5. **Dynamiczny Trailing Stop:**

   * Wdrożenie ruchomego Stop-Lossa zabezpieczającego wypracowany zysk.