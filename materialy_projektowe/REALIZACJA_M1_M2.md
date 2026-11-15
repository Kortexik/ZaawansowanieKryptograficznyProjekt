# Realizacja M1 i M2 Konrada

Zakres wynika z `PLAN_PROJEKT_1.md`. Użytkownik dostarcza `data/rockyou.txt`. Nie implementujemy modelu, treningu ani generowania, które należą do Kacpra. Bez operacji Git/GitHub.

## Decyzje techniczne

Python 3.10 lub nowszy, tylko biblioteka standardowa. Wejście czytamy jako bajty. Przyjmujemy drukowalne ASCII o długości od 1 do 64 znaków, zachowując spacje i wielkość liter. Odrzucenia liczymy w statystykach. Zakres można zmienić argumentami długości; alfabet pozostaje ASCII.

Zliczanie duplikatów wykonujemy w tymczasowej bazie SQLite, żeby nie przechowywać całego RockYou w pamięci. Skrót hasła z ziarnem wyznacza kolejność wyboru próby do miliona unikalnych wartości. Wybraną próbę dzielimy 80/10/10, z minimum jednym rekordem na część. Limit próby zapobiega sytuacji, w której 100 tys. kandydatów nie może matematycznie osiągnąć 15% na zbyt dużym teście. Słownik bazowy powstaje wyłącznie z treningu, według częstości.

Tokenizer ma stały alfabet ASCII oraz PAD, BOS i EOS. Dane treningowe i walidacyjne są zwykłymi plikami tekstowymi. Odpowiedzi, losowe sole i hashe testowe zapisujemy osobno dla oceniającego. Ocena porównuje zamknięty słownik z odpowiedziami, bez udostępniania soli generatorowi.

## Kolejność prac

- [x] Napisać testy rozłączności i powtarzalności podziału, zachowania spacji, tokenizera, rankingu słownika oraz znanego wyniku oceny.
- [x] Uruchomić testy przed implementacją i potwierdzić brak wymaganych funkcji.
- [x] Dodać tokenizer, przygotowanie danych i ocenę z obsługą błędów wejścia.
- [x] Uruchomić testy i oba polecenia na tymczasowych danych.
- [x] Opisać format danych dla Kacpra, model zagrożeń i komendy użytkownika.
- [x] Sprawdzić całość i podać wyniki. Pełne RockYou sprawdza użytkownik po dodaniu pliku.

## Wynik sprawdzenia

12 testów przechodzi. Sprawdzono też polecenia przygotowania i oceny na 100 tys. sztucznych haseł, pełny budżet kandydatów oraz odmowę nadpisania wyników. Niezależny przegląd nie wykazał pozostałych istotnych usterek. Po dodaniu RockYou wykonano próbę na 10 tys. wierszy i pełne przygotowanie danych. Przeczytano 14 344 391 wierszy, uzyskano 14 329 011 poprawnych unikalnych haseł i wybrano próbę miliona. Podział wynosi 800 tys. treningowych, 100 tys. walidacyjnych i 100 tys. testowych. Niezależna kontrola wszystkich plików potwierdziła rozłączność zbiorów, zgodność 100 tys. hashy z solami i odpowiedziami, bazę wyłącznie z treningu oraz sumę kontrolną pliku źródłowego. Wyniki znajdują się w `data/processed`.
