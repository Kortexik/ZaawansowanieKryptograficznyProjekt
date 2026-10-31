# Projekt 1 — plan realizacji dla osób A i B

**Temat:** Detekcja słabych haseł i generowanie słowników za pomocą sieci LSTM.  
**A:** Ty. **B:** Kacper.  
**Źródło:** `ZTKIK_PROJEKT_2026_2027.docx`, Projekt 1 oraz wspólne wymagania metodologiczne i zasady oceniania.  
**Status:** plan. Nie rozpoczęto implementacji ani pobierania danych. Bez operacji Git/GitHub.

## 1. Zakres i rezultat

Przepływ projektu: **RockYou → przygotowanie danych → znakowy LSTM w PyTorch → słownik 100 tys. haseł → ocena trafień → raport i obrona.**

Wymagania dokumentu:

- RockYou jako dane; dokument wskazuje SecLists jako źródło.
- Preprocessing i tokenizacja znakowa w Pythonie, trening LSTM w PyTorch.
- Wygenerowanie 100 tys. haseł i sprawdzenie trafień.
- Cel: trafienie co najmniej 15% haseł z próbki testowej nieobecnych w słowniku bazowym.
- Formalny model zagrożeń, grupa kontrolna, poprawny podział danych i jawne hiperparametry.
- Modularny kod, `requirements.txt`, raport w strukturze IEEE/ACM, wykresy i literatura.
- Obrona indywidualna, macierz wkładu oraz historia pracy w Git.

Propozycje organizacyjne, a nie wymagania dokumentu:

- **6 tygodni od rozpoczęcia, 75 roboczogodzin łącznie: A — 37 h, B — 38 h.** Czas oczekiwania na trening poza oszacowaniem. Termin oddania trzeba jeszcze ustalić.
- Skrypty Python i demonstracyjny notebook. Bez aplikacji webowej i serwera.
- PyTorch, NumPy, pandas, matplotlib. CPU do prób; GPU/Colab do większego treningu, jeśli będzie potrzebny.
- Właściciel wykonuje zadanie, druga osoba sprawdza wynik. Ty poznajesz również część Kacpra, a Kacper — Twoją.

## 2. Trzy kwestie do wyjaśnienia z prowadzącym

**Odpowiada A, B sprawdza propozycje.** Dane i model można przygotowywać podczas oczekiwania; sporne decyzje oznaczyć jako otwarte.

### Sól i model zagrożeń

Dokument podaje „bazę zaszyfrowanych haseł (np. SHA-256) bez znajomości soli”. SHA-256 jest funkcją skrótu, nie szyfrem. Nieznana sól uniemożliwia zwykłe sprawdzanie kandydatów przez porównanie hashy; LSTM nie usuwa tej przeszkody.

**Pytanie:** czy dopuszczalny jest eksperyment offline z SHA-256 bez soli albo ze znaną solą przypisaną do rekordu?

Propozycja: własne hashe wydzielonych haseł testowych, SHA-256 bez soli. Jawne odpowiedzi testowe służą tylko do końcowej oceny. Wariant ze znaną solą ewentualnie jako rozszerzenie. Nie przedstawiać tego jako łamania hashy z nieznaną solą.

Model zagrożeń powinien wskazać: przeciwnika offline, jego dostęp do hashy w uzgodnionym wariancie, znajomość algorytmu i kodu zgodnie z zasadą Kerckhoffsa, brak dostępu do odpowiedzi testowych podczas treningu, budżet prób i kryterium sukcesu.

### Słownik bazowy i budżet

**Pytanie:** co dokładnie oznacza „słownik bazowy” oraz czy 100 tys. oznacza losowania, czy unikalne kandydaty?

Propozycja: najczęstsze hasła wyłącznie z treningu, do 100 tys. unikalnych pozycji; LSTM generuje 100 tys. unikalnych, poprawnych kandydatów. Raport zawiera też liczbę wszystkich losowań, duplikatów i odrzuceń. Jeśli danych bazowych jest mniej, podać to i dodatkowo porównać metody przy wspólnym mniejszym budżecie.

Nie stosować całego RockYou jako słownika bazowego, jeśli test pochodzi z RockYou — zawierałby odpowiedzi testowe. Ograniczenia proponowanego porównania opisano w sekcji 5.

### Detekcja słabych haseł

Tytuł obejmuje detekcję, ale etapy dokumentu skupiają się na generowaniu.

**Pytanie:** czy wystarczy demonstrator prawdopodobieństwa/przewidywalności hasła według LSTM oraz obecności w wygenerowanym słowniku, czy wymagany jest osobny klasyfikator „słabe/silne”?

Propozycja: prosty demonstrator, bez dodatkowego klasyfikatora. Wynik modelu i brak trafienia w skończonym słowniku nie stanowią dowodu bezpieczeństwa hasła. Osobny klasyfikator wymaga uzgodnienia etykiet i metryki.

## 3. Podział odpowiedzialności

| Obszar | Wykonuje | Sprawdza |
|---|---|---|
| Wymagania, kontakt z prowadzącym, model zagrożeń | A | B |
| Dane, czyszczenie, podział, statystyki, tokenizer | A | B |
| Architektura LSTM, trening, checkpointy | B | A |
| Generowanie słownika i demonstrator | B | A |
| Słownik bazowy, metryki, wykresy, interpretacja | A | B |
| Eksperymenty: uruchomienia i logi modelu | B | A |
| Raport: dane, ocena, wyniki, ograniczenia | A | B |
| Raport: model, trening, generowanie, odtworzenie | B | A |
| Macierz wkładu i obrona | Każdy własną część | Wzajemnie |
| Wszystkie operacje Git/GitHub | A — ręcznie | B dostarcza opis swojego wkładu |

## 4. Milestony

Godziny oznaczają aktywną pracę. Terminy względne — do dostosowania do terminu oddania.

| Etap | Termin | A | B | Warunek zakończenia | Zależność |
|---|---|---:|---:|---|---|
| M0. Zakres i metoda | Początek tyg. 1 | 2 h | 2 h | Spisany eksperyment, metryka i otwarte pytania | — |
| M1. Dane | Koniec tyg. 1 | 8 h | 4 h | Rozłączne zbiory, tokenizer, statystyki | M0 |
| M2. Mały eksperyment | Koniec tyg. 2 | 4 h | 8 h | Cały przepływ działa na małej próbce | M1 |
| M3. Trening | Koniec tyg. 3 | 3 h | 10 h | Model i generowanie wybrane na walidacji | M2 |
| M4. Słowniki | Koniec tyg. 4 | 6 h | 6 h | Słowniki i zamrożona procedura oceny | M3 |
| M5. Wyniki | Koniec tyg. 5 | 9 h | 2 h | Metryki, wykresy i kontrola poprawności | M4 |
| M6. Oddanie | Koniec tyg. 6 | 5 h | 6 h | Raport, demonstracja, wkład i próba obrony | M5 |
| **Razem** | **6 tygodni** | **37 h** | **38 h** | **75 roboczogodzin** | |

### M0 — zakres i metoda

- [ ] **A:** spisać wymagania, ustalić termin oddania i przekazać prowadzącemu pytania z sekcji 2.
- [ ] **A:** opisać model zagrożeń oraz formalną metrykę.
- [ ] **B:** zaproponować mały model znakowy, sprawdzić dostępność CPU/GPU i budżet obliczeń.
- [ ] **B:** zaproponować zapis konfiguracji, ziaren losowania i wyników.
- [ ] **A + B:** uzgodnić minimalny zakres, definicję testu i sposób dokumentowania wkładu.

**Odbiór:** obaj jednakowo rozumiecie wejście, wyjście i próg 15%. Otwarte decyzje są zapisane.

### M1 — dane gotowe do treningu

- [ ] **A:** pobrać RockYou z uzgodnionego źródła; zapisać adres, datę, sumę kontrolną i zasady wykorzystania.
- [ ] **A:** sprawdzić kodowanie, liczbę rekordów, częstości, duplikaty i długości. Ustalić zakres długości i znaków; policzyć odrzucenia.
- [ ] **A:** usuwać końce linii zgodnie z formatem, zachowując spacje należące do hasła i wielkość liter. Bez bezwarunkowego `strip()`, zamiany na małe litery i cichego zastępowania błędnych znaków.
- [ ] **A:** podzielić unikalne wartości, proponowane 80/10/10, ze stałym ziarnem. To samo hasło nie może występować w treningu, walidacji i teście; częstości zachować osobno.
- [ ] **A:** przygotować tokenizer znakowy ze znacznikami początku, końca i dopełnienia. Alfabet ustalić z treningu; obsługę nieznanych znaków w pozostałych zbiorach jawnie opisać i policzyć.
- [ ] **B:** sprawdzić rozłączność zbiorów i format tokenizera; przygotować ładowanie partii i maskowanie dopełnienia w stracie.

**Przekazanie A → B:** trening, walidacja, tokenizer, opis kodowania, format batcha, statystyki i ziarno podziału. Test odłożyć do końcowej oceny.

**Odbiór:** przygotowanie jest powtarzalne, przecięcia zbiorów puste, dane pasują do modelu.

### M2 — mały eksperyment od początku do końca

- [ ] **B:** zbudować model: embedding → LSTM → warstwa przewidująca kolejny znak; trenować na małej próbce.
- [ ] **B:** dodać zapis/odczyt wag, konfiguracji i tokenizera oraz generowanie z końcem sekwencji i limitem długości.
- [ ] **A:** przygotować obliczanie trafień oraz małe przykłady z ręcznie znanymi wynikami.
- [ ] **A:** sprawdzić tokenizer, maskowanie dopełnienia i działanie ponownie wczytanego modelu.
- [ ] **A + B:** uruchomić kompletny przepływ, zmierzyć czas treningu i generowania; zdecydować o sprzęcie dla M3.

**Odbiór:** dane → trening → zapis → odczyt → generowanie → metryka działa bez ręcznego poprawiania wyników. To kontrola działania, nie końcowy wynik naukowy.

### M3 — trening i wybór modelu

- [ ] **B:** przetestować model podstawowy i maksymalnie dwa uzasadnione warianty. Zapisać warstwy, dropout, optimizer, learning rate, batch size, epoki i ziarna.
- [ ] **B:** rejestrować straty treningowe/walidacyjne, czas i sprzęt; zapisywać najlepszy checkpoint według wcześniej ustalonej reguły.
- [ ] **A:** sprawdzić logi pod kątem przeuczenia i porównać konfiguracje wyłącznie na walidacji.
- [ ] **B:** dobrać temperaturę oraz ustawienia generowania na walidacji przy stałym budżecie kandydatów.
- [ ] **A + B:** zamrozić model i ustawienia. Powtórzenia z innymi ziarnami wykonać w ramach dostępnych zasobów; przy pojedynczym przebiegu zaznaczyć ograniczenie.

**Przekazanie B → A:** checkpoint, tokenizer, konfiguracja, logi, opis sprzętu i instrukcja odtworzenia.

**Odbiór:** wybór ma uzasadnienie w walidacji; test nie brał udziału w strojeniu.

### M4 — słowniki i przygotowana ocena

- [ ] **B:** wygenerować 100 tys. unikalnych, poprawnych kandydatów. Zachować kolejność pierwszego wystąpienia, liczbę losowań, duplikatów, odrzuceń i czas.
- [ ] **B:** przed generowaniem ustalić limit czasu/liczby losowań. Jeśli nie uda się uzyskać 100 tys. pozycji, jawnie zgłosić niedobór i wrócić do walidacji; nie uzupełniać słownika odpowiedziami testowymi.
- [ ] **B:** przygotować demonstrator przewidywalności w zakresie uzgodnionym w M0.
- [ ] **A:** przygotować słownik bazowy z treningu oraz sprawdzić zgodność budżetów, kodowania i filtrów.
- [ ] **A:** przygotować ocenę przy 1 tys., 10 tys., 50 tys. i 100 tys. kandydatów, bez zmiany kolejności generowania.
- [ ] **A + B:** zamknąć procedurę oceny przed otwarciem testu. Kandydaty obecne w treningu raportować; nie odzyskiwać po fakcie zużytego przez nie budżetu.

**Odbiór:** słowniki gotowe, procedura sprawdzona na danych kontrolnych, ustawienia zamrożone.

### M5 — wyniki końcowe

- [ ] **A:** uruchomić ocenę na odłożonym teście; zapisać liczniki, mianowniki i konfigurację.
- [ ] **A:** policzyć trafienia LSTM, bazowe, nowe względem bazy i łączne pokrycie przy równych budżetach.
- [ ] **A:** przygotować wykresy uczenia, trafień względem budżetu, długości haseł oraz tabelę czasu i duplikatów.
- [ ] **B:** niezależnie przeliczyć małą próbkę wyników i sprawdzić wybrany przebieg generowania.
- [ ] **A:** w uzgodnionym wariancie wykonać demonstrację na własnych hashach testowych; potwierdzić zgodność z oceną jawną i identyczne kodowanie bajtów.
- [ ] **A + B:** opisać wynik również poniżej 15%. Strojenie po zobaczeniu testu wymaga nowego niezależnego testu albo jawnego oznaczenia dalszych wyników jako eksploracyjnych.

**Odbiór:** wyniki da się przeliczyć z zapisanych artefaktów; wiadomo, czy cel został osiągnięty, na jakiej populacji i przy jakim koszcie.

### M6 — raport, demonstracja i obrona

- [ ] **A:** opracować dane, model zagrożeń, ocenę, wyniki i ograniczenia.
- [ ] **B:** opracować architekturę, trening, generowanie i instrukcję odtworzenia.
- [ ] **A + B:** połączyć raport: abstrakt, wprowadzenie, literatura, model zagrożeń, metoda, eksperymenty, wyniki, ograniczenia, wnioski, bibliografia.
- [ ] **B:** przygotować demonstrację i prezentację; **A:** sprawdzić zgodność liczb z raportem.
- [ ] **B:** uruchomić projekt według instrukcji w nowym środowisku; **A:** skontrolować pakiet oddania.
- [ ] **A + B:** uzupełnić macierz wkładu i przeprowadzić wzajemną próbę obrony: Ty wyjaśniasz również część Kacpra, a Kacper — Twoją.

**Odbiór:** raport i demonstracja pokazują te same wyniki, projekt można odtworzyć, wkład obu osób jest udokumentowany.

## 5. Metryki i granice wnioskowania

Definicje ustalić przed oceną:

- `T` — unikalne hasła testowe, rozłączne z treningiem i walidacją.
- `D` — słownik bazowy wyłącznie z treningu.
- `G_k` — pierwsze `k` unikalnych, poprawnych kandydatów LSTM w kolejności generowania.
- `T_nowe = T \ D` — hasła testowe nieobecne w bazie.

**Główna metryka:** `trafienia_nowe@100k = |G_100000 ∩ T_nowe| / |T_nowe|`. Cel: co najmniej `0,15`. Pusty mianownik oznacza metrykę niezdefiniowaną, nie 0% ani 100%.

W proponowanym podziale `D` pochodzi z treningu, zatem `T_nowe = T`, a trafienia bazowe wyniosą zero z definicji. Eksperyment mierzy **generowanie niewidzianych haseł**; nie dowodzi ogólnej przewagi LSTM nad zwykłym słownikiem w rzeczywistym audycie.

Jeśli prowadzący oczekuje realistycznego porównania łącznego pokrycia, uzgodnić osobny, niezależny korpus oceny, w którym mogą pojawić się hasła znane bazie. To dodatkowy eksperyment, nie zamiennik głównej metryki.

| Miara dodatkowa | Sposób oceny |
|---|---|
| Pokrycie testu | `|G_k ∩ T| / |T|` dla ustalonych budżetów |
| Pokrycie bazowe | `|D ∩ T| / |T|` |
| Pokrycie łączne | `|(D ∪ G_k) ∩ T| / |T|` |
| Odtwarzanie znanych haseł | Udział kandydatów obecnych w treningu |
| Koszt generowania | Losowania, duplikaty, odrzucenia i czas |
| Koszt obliczeń | Czas treningu, sprzęt, czas sprawdzania |

Przy każdym procencie podać liczbę trafień i celów. Wynik ważony częstością haseł, jeśli powstanie, raportować osobno od wyniku dla unikalnych wartości.

## 6. Proponowany podział plików na etap implementacji

To propozycja przyszłego układu — nie utworzono kodu ani pustych plików.

| Plik / katalog | Właściciel | Zawartość |
|---|---|---|
| `README.md` | A | Opis i uruchomienie eksperymentu |
| `requirements.txt`, `config/` | B | Zależności i konfiguracje |
| `src/prepare_data.py`, `src/tokenizer.py` | A | Dane, podział, kodowanie |
| `src/model.py`, `src/train.py` | B | LSTM i trening |
| `src/generate.py` | B | Słownik i statystyki generowania |
| `src/evaluate.py` | A | Metoda bazowa i metryki |
| `tests/` | A/B | Rozłączność, tokenizer, metryki, zapis modelu |
| `notebooks/` | B | Demonstracja |
| `data/raw/`, `data/processed/` | A | Dane lokalne |
| `artifacts/` | B | Wagi, konfiguracje i słowniki |
| `results/` | A | Tabele i wykresy |
| `materialy_projektowe/` | A/B | Ustalenia, raport i macierz wkładu |

Pełnego RockYou, list haseł i dużych checkpointów nie dodawać automatycznie do repozytorium. Instrukcja powinna pozwalać odtworzyć je lokalnie. Materiałów z umiejętności asystenta nie zapisywać w `docs/`; ten plan zapisano w katalogu głównym, ponieważ `.codex` jest objęty ograniczeniem zapisu.

## 7. Współpraca i dokumentowanie wkładu

- Początek tygodnia: wybrać zadania i warunek odbioru milestone'u.
- Środek tygodnia: krótko omówić blokady i formaty przekazywanych danych.
- Koniec tygodnia: druga osoba odtwarza rezultat; zapisujecie wynik odbioru.
- Raport uzupełniać od M0. Zmiany tokenizera, danych i formatu checkpointu uzgadniać przed wdrożeniem.

Przyszła macierz wkładu powinna mieć kolumny: **osoba, zadanie, artefakt/plik, dowód sprawdzenia, osoba sprawdzająca, data, odniesienie do historii pracy**. Każdy prowadzi własne wpisy.

Dokument przyznaje 30% oceny za indywidualną obronę i macierz wkładu. Kod i Git stanowią kolejne kryterium o wadze 15%. Jeśli cała historia wskazuje wyłącznie A, może być trudniej wykazać wkład B. Uzgodnijcie z prowadzącym dokumentowanie rzeczywistego autorstwa, gdy operacje wykonuje A; bez fikcyjnego przypisywania zmian.

## 8. Ryzyka i ograniczanie zakresu

| Ryzyko | Reakcja | Odpowiada |
|---|---|---|
| Niejasna sól lub metryka | Wyjaśnić w M0; nie zamykać spornego wariantu eksperymentu | A |
| Zbyt wolny trening | Pomiar w M2; mniejszy model/próba rozwojowa, potem GPU według potrzeby | B |
| Wycieki przez duplikaty | Podział po unikalnych wartościach i kontrola przecięć | A |
| Przeuczenie lub mała różnorodność | Walidacja, ograniczone warianty, pomiar duplikatów | B |
| Wynik poniżej 15% | Uczciwy raport i analiza przyczyn; bez dopasowywania do testu | A/B |
| Brak czasu | Odrzucić interfejs i dodatkowe modele; chronić ocenę i raport | A/B |
| Niejasny wkład | Macierz i dowody od początku, uzgodnione autorstwo | A/B |

## 9. Lista odbioru projektu

- [ ] Uzgodniono sól, słownik bazowy, budżet i zakres detekcji.
- [ ] Opisano model zagrożeń i kryterium sukcesu.
- [ ] Dane są rozłączne; opisano źródło, kodowanie i odrzucenia.
- [ ] Działa LSTM w PyTorch; zapisano wagi, tokenizer i konfigurację.
- [ ] Uzyskano wymagany budżet kandydatów i opisano koszt generowania.
- [ ] Są metoda bazowa, metryki, wykresy i jawny wynik względem 15%.
- [ ] Test nie służył do strojenia modelu i generowania.
- [ ] Instrukcja i `requirements.txt` pozwalają odtworzyć projekt.
- [ ] Raport IEEE/ACM zawiera wyniki, ograniczenia i zweryfikowaną bibliografię.
- [ ] Demonstracja i raport używają tych samych wyników.
- [ ] Każdy potrafi wyjaśnić całość i udokumentować własny wkład.
- [ ] Wymagane dowody historii pracy przygotowano ręcznie.

**Pierwszy krok A:** ustalić termin oddania i wyjaśnić pytania z sekcji 2.  
**Pierwszy krok B:** sprawdzić zasoby i zaproponować mały LSTM.  
**Pierwszy wspólny odbiór:** M0 — uzgodniona definicja eksperymentu.
