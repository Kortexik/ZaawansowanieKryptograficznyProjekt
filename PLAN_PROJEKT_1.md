# Projekt 1. Plan wykonania

Temat projektu to detekcja słabych haseł i generowanie słowników za pomocą sieci LSTM. Projekt realizują Konrad i Kacper.

Plan opiera się na Projekcie 1 z dokumentu `ZTKIK_PROJEKT_2026_2027.docx`. Przyjmujemy jeden sposób realizacji opisany poniżej. Określa on podział pracy i kolejność etapów. Szczegóły implementacji dobiera osoba odpowiedzialna za daną część.

## Cel

Przygotowujemy dane RockYou, trenujemy LSTM w PyTorch i generujemy 100 tys. haseł. Sprawdzamy, ile haseł testowych udało się odgadnąć.

Cel z polecenia to co najmniej 15% trafień wśród haseł testowych nieobecnych w słowniku bazowym. Podajemy rzeczywisty wynik, również jeśli będzie niższy.

## Nieznana sól i ocena trafień

Atakujący nie zna soli. Kacper przygotowuje model i generuje słownik bez dostępu do haseł testowych ani ich soli. Konrad przygotowuje osobny program oceniający, który zna prawidłowe hasła i sole. Sprawdza trafienia dopiero po ustaleniu końcowego słownika. Nie udostępnia modelowi odpowiedzi ani możliwości sprawdzania kolejnych kandydatów podczas generowania.

Mierzymy, ile prawidłowych haseł znalazło się w słowniku. Nie twierdzimy, że LSTM odgaduje sól lub że atakujący potrafi sam rozpoznać trafienie. Generowanie słownika i niezależna ocena są dwiema częściami jednego eksperymentu. Realizację zaczynamy od M1.

## Podział pracy

- Konrad odpowiada za dane, przygotowanie sposobu oceny, model zagrożeń oraz analizę wyników.
- Kacper odpowiada za model LSTM, trening, generowanie haseł oraz demonstrację działania.
- Raport dzielimy według wykonanych części. Każdy sprawdza również pracę drugiej osoby i przygotowuje się do obrony całości.

## Milestony

Zakładamy sześć tygodni pracy. Etapy następują po sobie, a zadania Konrada i Kacpra w danym etapie można wykonywać równolegle.

| Etap | Konrad | Kacper | Wynik etapu |
|---|---|---|---|
| M1. Przygotowanie | Pobiera i porządkuje dane. Przygotowuje podział danych, tokenizację, model zagrożeń i zasady oceny. | Przygotowuje środowisko i model LSTM. Sprawdza, czy może korzystać z danych od Konrada. | Dane są gotowe, a model może je wczytać. |
| M2. Pierwszy przebieg | Przygotowuje słownik bazowy i obliczanie trafień. Sprawdza ocenę na małym przykładzie. | Trenuje model na małej próbce i generuje pierwsze hasła. | Całość działa od przygotowanych danych do wyniku oceny. |
| M3. Trening | Sprawdza poprawność eksperymentu i analizuje wyniki walidacji. | Przeprowadza główny trening i wybiera model na podstawie walidacji. | Model jest gotowy do generowania słownika. |
| M4. Generowanie i ocena | Ocenia trafienia na zbiorze testowym, przygotowuje wykresy i wnioski. | Generuje 100 tys. haseł, przygotowuje demonstrację i sprawdza obliczenia Konrada. | Są słownik, wyniki i porównanie z celem 15%. |
| M5. Raport i obrona | Opisuje dane, model zagrożeń, ocenę, wyniki i ograniczenia. | Opisuje model, trening i generowanie. Przygotowuje pokaz działania. | Raport jest kompletny, demonstracja działa, obaj potrafią wyjaśnić projekt. |

## Współpraca

Konrad przekazuje Kacprowi przygotowane dane i opis ich formatu. Kacper przekazuje Konradowi wygenerowany słownik oraz wyniki treningu potrzebne do oceny i raportu.

Danych testowych nie używamy do dobierania modelu. Po każdym etapie druga osoba sprawdza rezultat, zanim przejdziemy dalej.

## Pierwsze zadania

1. Konrad pobiera RockYou i przygotowuje małą próbkę danych.
2. Kacper przygotowuje środowisko i model, który będzie mógł tę próbkę wczytać.
3. Konrad przygotowuje sposób liczenia trafień, a Kacper uruchamia pierwszy trening.
4. Konrad i Kacper sprawdzają pierwszy wynik i przechodzą do głównego eksperymentu.
