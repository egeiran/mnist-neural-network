# Sette opp mnist.eivindgeiran.no

Fire ting, i denne rekkefølgen. Regn med ti minutter.

## 1. Nytt prosjekt på Vercel

Importer `egeiran/mnist-neural-network` som et **nytt** Vercel-prosjekt (ikke
det samme som eivindgeiran.no — dette er et eget deploy).

Den ene innstillingen som må endres fra standard:

| Felt | Verdi |
|---|---|
| **Root Directory** | `web` |

Resten oppdager Vercel selv (Next.js, `npm run build`). Ingen miljøvariabler
trengs — siden er helt statisk og har ingen hemmeligheter.

## 2. Domenet

I Vercel-prosjektet: **Settings → Domains → Add** → `mnist.eivindgeiran.no`.

Vercel gir deg en CNAME-verdi. Legg den inn hos den som holder DNS for
eivindgeiran.no:

```
Type    Name     Value
CNAME   mnist    cname.vercel-dns.com
```

Dette er samme oppsett som `nhl-ml`, `tilbud` og `towerdefense` allerede har, så
DNS-en din har mønsteret fra før. Sertifikatet ordner Vercel automatisk når
oppslaget svarer, vanligvis innen et par minutter.

## 3. Kapittelmerkene i filmen

Filmen ligger allerede inne — `youtubeId` i `web/src/lib/site.ts` peker på
[`3KQHb3Rx8PM`](https://youtu.be/3KQHb3Rx8PM), og videoseksjonen viser den.

Det som **ikke** er gjort, er kapitlene. Lista i `site.ts` har de planlagte
tidene fra `manus.md`, ikke tidene i den ferdige filmen. Med ekte tale får hver
scene den lengden lyden faktisk har, så de siste kapitlene ligger antakelig et
stykke unna. Derfor er de skjult bak `chaptersVerified: false`.

Slik slår du dem på:

1. Se gjennom filmen og noter hvor hver scene faktisk starter.
2. Rett `at`-verdiene i `SITE.chapters` (sekunder fra start).
3. Sett `chaptersVerified: true`.
4. Commit og push — Vercel bygger på nytt av seg selv.

Lim gjerne samme liste inn i YouTube-beskrivelsen på formen `0:00 The problem`,
én per linje med 0:00 først, så får videoen kapittelmerker der også.

## 4. Prosjektkortet på eivindgeiran.no

Åpne `lib/copy.ts` i `egeiran/eivindgeiran` og legg til en oppføring i
`projects`-lista — **to steder**, én under `no` og én under `en`. Jeg ville lagt
den øverst, foran NHL-modellen: den har en demo man kan ta på, og det er det
sterkeste kortet i stokken.

Norsk (`no.projects`):

```ts
{
  name: "Nevralt nettverk fra bunnen av",
  tag: "ML",
  url: "https://github.com/egeiran/mnist-neural-network",
  webUrl: "https://mnist.eivindgeiran.no/",
  link: "GitHub",
  openLabel: "Åpne prosjektet",
  description:
    "784 → 128 → 10 i ren NumPy, uten ML-bibliotek. Backprop derivert for hånd og verifisert mot numeriske gradienter. Tegn et siffer på siden, så kjører de ekte trente vektene i nettleseren din.",
  stack: ["Python", "NumPy", "Manim", "Next.js"],
},
```

Engelsk (`en.projects`):

```ts
{
  name: "Neural network from scratch",
  tag: "ML",
  url: "https://github.com/egeiran/mnist-neural-network",
  webUrl: "https://mnist.eivindgeiran.no/",
  link: "GitHub",
  openLabel: "Open project",
  description:
    "784 → 128 → 10 in plain NumPy, no ML library. Backpropagation derived by hand and verified against numerical gradients. Draw a digit on the site and the real trained weights run in your browser.",
  stack: ["Python", "NumPy", "Manim", "Next.js"],
},
```

`LivePreview`-komponenten henter forhåndsvisningen fra `webUrl` automatisk, så
kortet viser den ekte siden så snart domenet svarer. Ikke legg dette inn før
steg 2 er ferdig, ellers står kortet med en tom ramme.

---

## Hvis noe ikke stemmer

**Bygget feiler med «Module not found: @/data/run.json».** `web/src/data/run.json`
er sjekket inn, men hvis du har kjørt `make clean` eller retrent, kjør
`python tools/export_web.py` fra rota og commit resultatet på nytt.

**Demoen sier «Klarte ikke laste vektene».** Da har ikke
`web/public/model/mnist-784-128-10.f16` blitt med i deployet. Sjekk at fila
ligger i git (`git ls-files web/public/model`) — den er binær på 199 KB og er
lett å miste i en `.gitignore`-regel.

**Demoen gjetter feil hele tiden.** Det er nesten alltid forbehandlingen, ikke
modellen. Kjør verifiseringen i README-en (`tools/check_web_model.*`) — hvis den
er grønn, regner nettleseren riktig, og feilen ligger i hvordan tegningen
normaliseres i `web/src/lib/preprocess.ts`.
