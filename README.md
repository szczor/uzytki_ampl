Model mozna uruchomic za pomoca glpsol:

```
glpsol -m model.mod -d testmini.dat -o uzytki.sol
```

A nastepnie wygenerowac wizualizacje

```
python sol_parser.py
```
stworzona wizualizacje wyniku mozna zobazyc w folderze wykresy.