Model mozna uruchomic za pomoca glpsol:

```
glpsol -m model.mod -d testmini.dat -o uzytki.sol
```

A nastepnie wygenerowac wizualizacje

```
python sol_parser.py
```
stworzona wizualizacje wyniku mozna zobazyc w folderze wykresy.

## Konwersja danych wejściowych

Generowanie plików `.dat` z plików `.csv` odbywa sie za pomocą skryptu `csv2dat.py`. Skrypt przyjmuje dwa parametry do uruchomienia:

- Pierwszy (wymagany) to ścieżka do pliku z opisem danych wejściowych — zobacz przykładowy taki plik: `tabele/example.ini`
- Drugi (opcjonalny) to nazwa pliku `.dat` do wygenerowania. Jeżeli zostanie podany, to ustawienie `FileName` w sekcji `Output` zostanie zignorowany.

Przykładowe wywołanie:

```sh
python3 csv2dat.py tabele/example.ini uzytki.dat
```