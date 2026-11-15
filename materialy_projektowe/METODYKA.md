# Model zagrożeń i ocena M1/M2

Przeciwnik działa offline. Zna metodę, kod i model, ma hashe testowe, ale nie zna haseł ani przypisanych im soli. Kacper uczy LSTM wyłącznie na treningu, dobiera ustawienia na walidacji, następnie zamyka słownik kandydatów. Konrad dopiero wtedy otwiera odpowiedzi testowe i oblicza wynik. Zestaw danych oraz kod są jawne zgodnie z zasadą Kerckhoffsa; wydzielone odpowiedzi testowe pozostają poza procesem doboru modelu.

Każde testowe hasło ma niezależną losową sól długości 16 bajtów. Hash liczymy jako `SHA-256(salt_bytes + password_ascii)`. Plik `hashes.txt` zawiera wyłącznie hashe. Sole i odpowiedzi przechowuje `targets.jsonl`, którego Kacper nie używa do uczenia ani generowania. Program oceniający kontroluje zgodność zapisanych odpowiedzi z hashami.

Oceniamy obecność prawidłowych haseł w gotowym słowniku. Nie symulujemy odkrywania soli ani samodzielnej weryfikacji trafień przez przeciwnika. Oceniający zna odpowiedzi, dlatego może sprawdzić obecność haseł bez kosztownego przeliczania każdej pary sól/kandydat. Nie udostępnia tej wiedzy generatorowi. Wynik nie dowodzi złamania hashy z nieznaną solą.

Trening, walidacja i test są rozłączne według wartości hasła. Duplikaty z bazy źródłowej nie mogą trafić do różnych części. Zachowane częstości służą budowie słownika bazowego wyłącznie z treningu. Hasła spoza przyjętego alfabetu i długości odrzucamy. Z poprawnych wartości wybieramy próbę do miliona unikalnych haseł według kolejności wyznaczonej skrótem z ziarnem. Wyniki odnosimy do tej próby, nie do całego RockYou.

Niech `T` oznacza unikalne cele testowe, `D` słownik bazowy, a `G` pierwsze 100 tys. unikalnych poprawnych kandydatów. Niech `T_nowe` oznacza cele z `T` nieobecne w `D`. Główna metryka to `|G ∩ T_nowe| / |T_nowe|`. Próg z polecenia wynosi 15%. Pusty mianownik daje wynik niezdefiniowany. Raport podaje również liczbę trafień, wielkość testu, budżet, duplikaty i wynik bazowy.

Przy 100 tys. kandydatów górna granica trafień wynosi 100 tys. unikalnych haseł. Test z ponad 666666 celami uniemożliwiałby osiągnięcie 15%. Domyślny limit próby daje około 100 tys. celów testowych. Próg jest wtedy możliwy matematycznie, ale nadal zależy od modelu i danych.

W naszym podziale `D` pochodzi z treningu i nie przecina się z `T`. Zerowy wynik bazowy jest skutkiem konstrukcji eksperymentu, a nie dowodem przewagi LSTM. Gdyby potrzebne było szersze porównanie metod, wymagałoby osobnego projektu eksperymentu.

Etap M2 potwierdza działanie przygotowania i oceny na ręcznie policzonych danych. Nie potwierdza osiągnięcia 15% ani gotowości części Kacpra. Ocena zamkniętego słownika z LSTM należy do dalszych etapów.
