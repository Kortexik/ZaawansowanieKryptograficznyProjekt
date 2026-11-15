# M1 i M2 Konrada

Gotowe są przygotowanie danych, tokenizer, słownik bazowy i obliczanie trafień. Model LSTM, trening i generowanie należą do Kacpra i nie są jeszcze zaimplementowane.

Potrzebny jest Python 3.10 lub nowszy. Ta część nie wymaga instalowania bibliotek.

## Uruchomienie

Otwórz terminal w folderze projektu i dodaj bazę jako `data/rockyou.txt`.

Najpierw sprawdź program na pierwszych 10 tys. wierszy:

```bash
python3 -m src.prepare_data --limit 10000 --output data/proba
```

Po udanej próbie przygotuj cały plik:

```bash
python3 -m src.prepare_data
```

Wyniki trafią do `data/processed`. Program przeczyta cały plik i wybierze do eksperymentu maksymalnie milion unikalnych poprawnych haseł. Wypisze liczby haseł i utworzy `stats.json`. Podczas większego uruchomienia pokazuje postęp co 500 tys. wierszy. Zliczanie i sortowanie korzysta z tymczasowej bazy na dysku. Potrzebne jest wolne miejsce na bazę i pliki wynikowe.

Program nie nadpisuje istniejącego folderu z wynikami. Przy kolejnym uruchomieniu wybierz nowy folder przez `--output`, na przykład `data/proba2`. Uruchomienie z `--limit` służy sprawdzeniu działania, nie pomiarowi końcowej skuteczności.

## Sprawdzenie bez RockYou

```bash
python3 -m unittest discover -s tests -v
```

Testy same tworzą i usuwają małe dane w folderze tymczasowym. Nie zmieniają `data/rockyou.txt`. Sprawdzają rozłączność zbiorów, powtarzalność podziału, zachowanie spacji, tokenizer, ranking bazowy, hashe i ręcznie policzone trafienia.

## Przygotowane pliki

| Plik w folderze wynikowym | Przeznaczenie |
|---|---|
| `train.txt` | Unikalne hasła treningowe, jedno w wierszu |
| `val.txt` | Unikalne hasła walidacyjne |
| `tokenizer.json` | Alfabet i identyfikatory tokenów dla modelu Kacpra |
| `baseline.txt` | Do 100 tys. najczęstszych haseł wyłącznie z treningu |
| `stats.json` | Liczności, odrzucenia, podział, parametry i suma SHA-256 przeczytanych bajtów |
| `evaluation/hashes.txt` | Hash każdego hasła testowego, bez soli i odpowiedzi |
| `evaluation/targets.jsonl` | Odpowiedzi, sole i hashe, wyłącznie do końcowej oceny Konrada |

Do uczenia Kacper dostaje `train.txt`, `val.txt` i `tokenizer.json`. Plików z `evaluation/` nie używa do treningu, doboru ustawień ani generowania słownika. To rozdzielenie ról w eksperymencie, a nie mechanizm izolacji dostępu na komputerze.

## Przyjęta metodyka

- Wejście czytamy jako bajty. Akceptujemy drukowalne ASCII i długości od 1 do 64 znaków. Odrzucamy pozostałe rekordy i podajemy ich liczbę. Zachowujemy wielkość liter i spacje, usuwamy zakończenia LF/CRLF. `--min-length` i `--max-length` zmieniają zakres długości.
- Najpierw zliczamy wystąpienia. Według kolejności wyznaczonej skrótem hasła i ziarnem wybieramy próbę do miliona unikalnych wartości. Dzielimy ją w proporcji około 80/10/10. Dla bardzo małych zbiorów każda część dostaje minimum jeden rekord. Potrzeba co najmniej trzech różnych poprawnych haseł. `--max-passwords` zmienia limit próby. `selected_passwords` i `excluded_by_sample_limit` w statystykach podają rozmiar próby i liczbę pominiętych wartości.
- Ziarno podziału to `42`, zmieniane przez `--seed`. Te same dane i parametry dają te same podziały, tokenizer i słownik bazowy. Sole powstają losowo, więc hashe mogą różnić się między uruchomieniami.
- Słownik bazowy porządkujemy według malejącej częstości, przy remisie alfabetycznie. `--baseline-size` zmienia jego limit. Liczności pochodzą wyłącznie z wartości przypisanych do treningu.
- Suma `sha256_of_read_bytes` dotyczy przeczytanych bajtów. Bez limitu obejmuje cały plik, z `--limit` tylko odczytany początek. Próba na początku RockYou nie musi być reprezentatywna dla całego pliku.

## Tokenizer dla Kacpra

```python
from src.tokenizer import CharacterTokenizer

tokenizer = CharacterTokenizer.load("data/processed/tokenizer.json")
tokens = tokenizer.encode("Przyklad123", pad_to=66)
inputs = tokens[:-1]
targets = tokens[1:]
password = tokenizer.decode(tokens)
```

Alfabet ma 98 tokenów. `PAD=0`, `BOS=1`, `EOS=2`, pozostałe identyfikatory odpowiadają znakom ASCII od 32 do 126. Do długości hasła dochodzą dwa znaczniki. Domyślne maksymalne hasło z BOS/EOS ma zatem 66 tokenów. Model powinien pomijać PAD w funkcji straty, na przykład przez `ignore_index=tokenizer.pad_id`. `decode` przyjmuje listę liczb całkowitych, kończy na EOS i pomija BOS oraz PAD. Tensor z PyTorch można przekazać po `.tolist()`.

## Ocena słownika od Kacpra

Gdy Kacper wygeneruje gotowy plik tekstowy z jednym hasłem w wierszu, Konrad uruchamia:

```bash
python3 -m src.evaluate --candidates artifacts/generated.txt --output results/ocena.json
```

Ścieżka `artifacts/generated.txt` jest przykładem pliku dostarczanego przez Kacpra. Nie tworzymy teraz zastępczego generatora. Przy danych z innego folderu podaj odpowiednie `--targets` i `--baseline`. Polecenie `--help` wyświetla wszystkie argumenty.

Program bierze pierwsze 100 tys. unikalnych poprawnych kandydatów w kolejności pliku. Pomija puste wiersze i znaki spoza alfabetu, zachowuje spacje. Duplikaty nie zużywają kolejnego miejsca w budżecie. Statystyki kandydatów dotyczą odczytanego fragmentu, do osiągnięcia budżetu lub końca pliku. Krótszego słownika nie uzupełnia; zgłasza `budget_reached: false`. Wyniki procentowe zapisuje jako ułamki, np. `0.25` to 25%.

Główna metryka `new_hit_rate` to liczba trafionych haseł testowych nieobecnych w bazie podzielona przez liczbę wszystkich haseł testowych nieobecnych w bazie. Przy pustym mianowniku wynosi `null`. Cel jest osiągnięty tylko przy pełnym budżecie 100 tys. unikalnych kandydatów i wyniku co najmniej `0.15`.

Słownik 100 tys. pozycji może trafić najwyżej 100 tys. różnych celów. Przy ponad 666666 celach próg 15% byłby niemożliwy. Domyślna próba miliona haseł daje około 100 tys. celów testowych i usuwa tę przeszkodę. Nie gwarantuje osiągnięcia 15%. Po zmianie limitu trzeba uwzględnić ten górny pułap, a wynik zawsze odnosić do wybranej próby.

Przykład sprawdzany w testach: cele to `alpha`, `beta`, `gamma`, `delta`, baza zawiera `alpha`, a słownik zawiera `alpha`, `beta` i dwa nietrafione hasła. Zwykłe pokrycie to 2/4. Po wyłączeniu bazy główny wynik to 1/3. Powtórzenie `alpha` w pliku nie zmienia wyniku.

W przygotowanym rozłącznym podziale baza z treningu osiągnie na teście zero trafień z definicji. Ten eksperyment mierzy generowanie niewidzianych haseł. Nie dowodzi ogólnej przewagi nad słownikiem w rzeczywistym audycie.

Model zagrożeń i granice tej oceny opisano w `materialy_projektowe/METODYKA.md`. Program oceniający nie powinien być używany jako informacja zwrotna do strojenia modelu na teście.
