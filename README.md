# ddo-cli

ddo.py --- look up words in Den Danske Ordbog

A command-line interface for looking up words in the Danish online dictionary
Den Danske Ordbog which can be found at http://ordnet.dk/ddo

## Usage
    ddo.py [-S] [-s ...] [-v ...] <word>
    ddo.py (-h | --help)
    ddo.py --version

## Options
    -S                  Very short output (same as -ssss)
    -s                  Short output (add up to four s'es for shorter output).
    -h, --help          Show this screen.
    --version           Show version.
    -v                  Print info (-vv for printing lots of info (debug)).

## Example
    >./ddo.py behændig
    behændig [beˈhεnˀdi] adjektiv
    Bøjning: -t, -e || -ere, -st
    Oprindelse: fra middelnedertysk /behendich/, af /behende/, egentlig 'ved hånden'

    Betydninger:
    1. i stand til at bevæge sig let, smidigt og ubesværet; fiks på fingrene
    SE OGSÅ: _adræt_ | _fingernem_
    GRAMMATIK: almindelig som adverbium
    han smuttede behændigt foran en lastbil og undgik smidigt strømmen af
    cykler -- Kjeld Koplev og Marianne Koester: Smertesommeren (ungdomsbog) -
    Borgen, 1990.

    1.b som vidner om denne evne
    her i Europa har vi i de senere år ofte kunnet lægge ører til hans
    behændige bebop-klaverspil -- Berlingske Tidende (avis), 1990.

    2. i stand til at klare en given situation på en dygtig, snedig eller elegant måde
    SYNONYMER: _fiks_ | _ferm_
    Nægtes kan det heller ikke, at skolerne mildest talt ikke har været
    behændige i deres omgang med medierne -- Ritt Bjerregaard og Søren Mørch:
    Fyn med omliggende øer / Danmark - Gyldendal, 1989.

    2.b som vidner om denne evne
    han [roser] hendes behændige forstillelseskunst og list i vanskelige
    situationer -- Anne E. Jensen: Holberg og kvinderne eller Et forsvar for
    ligeretten - Gyldendal, 1984.

    Orddannelser:
    AFLEDNINGER: _behændighed_ sb. | _ubehændig_ adj.

## Todo

Word wrapping option to avoid too long lines

Parallel, multi-threaded fetching of URLS

ASCII color output on terminal using
[termcolor](https://pypi.python.org/pypi/termcolor).

Display word of the day

Play pronounciation sound files

Output to non-Unicode terminals

## License
Copyright (C) 2016 Thomas Boevith

License: GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO
WARRANTY, to the extent permitted by law.

For details please see LICENSE file.
