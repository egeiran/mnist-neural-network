# Å se på scener uten å vente

Kort oppsummert: `make preview` når du vil se scenen, `make still` når du bare
skal flytte på noe, `make watch` når du holder på med én scene en stund, og
`make play` når du vil prøve deg fram uten å rendre i det hele tatt.

Målt på denne maskinen, én scene i 480p:

| kommando | s04 (68 s film) | s02 (38 s film) |
|---|---|---|
| `make scene` (som før, med cache) | 14,8 s | 20,8 s |
| samme, uten cache + parallell encoder | 10,5 s | 14,5 s |
| `+ FAST=1` (kortere pauser) | 9,1 s | 12,4 s |
| `make still` (bare ett bilde) | 3,7 s | 6,2 s |

Klassenavnet kan du droppe: `make scene S=s04_sigmoid` tar alt som ligger i
fila (`-a`), og hver scenefil her har nøyaktig én klasse. `C=S04Sigmoid` virker
fortsatt hvis du vil peke ut én bestemt.

## De fire kommandoene

    make preview S=s04_sigmoid

Live OpenGL-vindu. Ingenting skrives til disk, ingen ffmpeg, ingen QuickTime som
spretter opp etterpå — scenen spilles rett i et vindu du kan panorere (dra) og
zoome (scroll) i mens den går. Den spilles i sanntid, så den er ikke *raskere*
enn en render, men du ser første bilde med én gang og slipper ventingen på slutten.
`FAST=1` er standard her, så en 68-sekunders scene tar 25 sekunder å se.

    make still S=s04_sigmoid
    make still S=s04_sigmoid N=0,12

Rendrer bare ett bilde til PNG og åpner det. Dette er den store gevinsten når du
holder på med plassering, farger, tekststørrelse — 4 sekunder mot 15. `N=0,12`
gir deg bildet slik det ser ut etter animasjon 12, så du kan sikte deg inn midt
i en scene.

    make watch S=s04_sigmoid
    make watch S=s04_sigmoid V=1

Rendrer på nytt hver gang du lagrer noe under `scenes/` eller `nn/`. Stillbilde
som standard, `V=1` gir video. Lagrer du mens en render går, drepes den og en ny
starter. Ctrl-C avslutter.

    make play

Lekegrinda: et levende vindu pluss et IPython-skall i terminalen som skriver rett
inn i vinduet. Her rendrer du ingenting — du prøver:

    self.add(digit_image(run()["x_test"][0]))
    self.play(FadeIn(body("hei")))
    self.clear()

`body`, `mono`, `run`, `digit_image`, fargene og resten fra `scenes/common.py`
ligger klart (og alt annet på `c.`). `rerun` kjører `construct()` på nytt, `exit`
avslutter. Lagrer du `scenes/sandbox.py` mens vinduet står åpent, kjøres scenen
automatisk på nytt — men endringer i `common.py` krever omstart, for den modulen
lastes ikke på nytt.

## Å lime kode fra editoren inn i det levende vinduet

Dette er trikset 3b1b bruker: han markerer en blokk i editoren og sender den inn
i skallet som allerede kjører, i stedet for å starte scenen på nytt. To måter her:

* Kopier blokken (⌘C), skriv `%paste` i IPython-skallet. Virker uten oppsett.
* Eller bind opp «Terminal: Run Selected Text in Active Terminal» i VS Code, så
  går markert kode rett inn i skallet med ett tastetrykk:

      { "key": "cmd+enter",
        "command": "workbench.action.terminal.runSelectedText",
        "when": "editorTextFocus" }

Legg gjerne `self.clear()` først i blokken du limer inn, så bygger du ikke oppå
det forrige forsøket.

## Skruene under

* `FAST=1` estimerer fortellerstemmen til en firedel av lengden, så pausene i
  scenen krymper. `SPEED=0.5` gir finkontroll, `FAST=0` gir ekte timing. Med
  `VOICEOVER=1` ignoreres begge — ekte lyd har den lengden den har.
* `N=3,6` rendrer bare animasjon 3 til 6. Manim må fortsatt regne seg gjennom
  scenen fram dit, men slipper å tegne og encode resten.
* `--disable_caching` er nå standard i alle render-målene og i `build.sh`.
  Det høres bakvendt ut, men manims cache hasher hele mobject-treet før hver
  animasjon, og i dette prosjektet — med 784 kvadrater i et rutenett — koster
  hashingen mer enn den sparer: en render der *alt* lå i cachen var tregere enn
  å rendre alt på nytt uten cache. Sett `TURBO=` for å få den gamle oppførselen.
* `--max-inflight-encoders 4` lar ffmpeg encode ferdig animasjon mens neste
  tegnes. Gratis noen prosent.
