/**
 * All tekst på siden, på begge språk. Én kilde — ingen tekst ligger gjemt inne
 * i en komponent.
 *
 * Tall står bevisst IKKE her. De kommer fra src/data/run.json, som genereres av
 * tools/export_web.py, slik at en ny treningskjøring oppdaterer tallene uten at
 * teksten rundt dem må skrives om.
 */

export type Lang = "no" | "en";

export interface Copy {
  meta: { title: string; description: string };
  nav: { repo: string; site: string; video: string; demo: string };
  hero: {
    eyebrow: string;
    title: string;
    lede: string;
    stats: { value: string; label: string }[];
  };
  demo: {
    title: string;
    lede: string;
    clear: string;
    examples: string;
    examplesHint: string;
    drawHint: string;
    empty: string;
    loading: string;
    error: string;
    verdict: string;
    activation: string;
    hidden: string;
    hiddenNote: string;
    preprocessed: string;
    preprocessNote: string;
    notProbabilities: string;
    offline: string;
  };
  video: { title: string; lede: string; play: string; missing: string; chapters: string };
  how: {
    title: string;
    lede: string;
    steps: { title: string; body: string }[];
    codeCaption: string;
    arch: { pixels: string; hidden: string; digits: string; weights: string };
  };
  gradcheck: { title: string; lede: string; caption: string; takeaway: string };
  training: {
    title: string;
    lede: string;
    axisEpoch: string;
    axisAcc: string;
    axisLoss: string;
    batchCaption: string;
    epochCaption: string;
  };
  learned: { title: string; lede: string; caption: string; legend: [string, string] };
  misses: {
    title: string;
    lede: string;
    said: string;
    was: string;
    sure: string;
    confusionTitle: string;
    confusionLede: string;
    confusionRow: string;
    confusionCol: string;
    confusionEmpty: string;
    topTitle: string;
    times: string;
  };
  honest: { title: string; body: string[] };
  footer: { built: string; source: string; back: string; colophon: string };
}

const no: Copy = {
  meta: {
    title: "Et nevralt nettverk fra bunnen av — Eivind Geiran",
    description:
      "784 → 128 → 10, skrevet i ren NumPy uten ML-bibliotek. Tegn et siffer og kjør de ekte trente vektene i nettleseren, og se filmen om hvordan det virker.",
  },
  nav: { repo: "Kode", site: "eivindgeiran.no", video: "Film", demo: "Prøv den" },
  hero: {
    eyebrow: "MNIST · NumPy · Manim",
    title: "Jeg bygget et nevralt nettverk fra bunnen av.",
    lede:
      "Ingen TensorFlow, ingen PyTorch, ingen scikit-learn — bare NumPy til matrisematematikken. Backprop er derivert for hånd og verifisert mot numeriske gradienter. Så laget jeg en film om hvordan det virker, animert i Manim. Nettverket under er ikke et bilde av en demo: det er de ekte vektene, og de kjører i nettleseren din.",
    stats: [
      { value: "97,47 %", label: "treffsikkerhet på testsettet" },
      { value: "101 770", label: "parametre" },
      { value: "0", label: "ML-bibliotek brukt" },
      { value: "1,0e−11", label: "avvik i gradientsjekken" },
    ],
  },
  demo: {
    title: "Tegn et siffer",
    lede:
      "Bruk musa eller fingeren. Nettverket regner mens du tegner. Ingenting sendes noe sted — de 101 770 parametrene lastes ned én gang (199 KB) og hele utregningen skjer på din egen maskin.",
    clear: "Tøm",
    examples: "Eller prøv et ekte MNIST-siffer:",
    examplesHint: "Disse kommer fra treningsbatchen som ligger lagret i run.npz.",
    drawHint: "Tegn her",
    empty: "Tegn et siffer, så begynner den å regne.",
    loading: "Laster vektene …",
    error: "Klarte ikke laste vektene. Prøv å laste siden på nytt.",
    verdict: "Nettverket sier",
    activation: "Utgangsaktivering",
    hidden: "Det skjulte laget",
    hiddenNote:
      "128 nevroner. Hver rute er ett av dem, og lysstyrken er hvor sterkt det fyrer akkurat nå. Dette er alt nettverket «vet» om sifferet ditt før det bestemmer seg.",
    preprocessed: "Slik ser nettverket det",
    preprocessNote:
      "Tegningen din beskjæres, skaleres til 20×20 og sentreres etter tyngdepunkt i et 28×28-felt — nøyaktig slik MNIST-bildene ble normalisert. Hopper man over dette steget, bommer nettverket systematisk, og det er forbehandlingen som er feil, ikke modellen.",
    notProbabilities:
      "Merk: utgangene summerer seg ikke til 1. Nettverket bruker sigmoid og kvadratfeil, ikke softmax og kryssentropi, så hver utgang er et uavhengig svar mellom 0 og 1. Det er et bevisst valg — mer om det nederst.",
    offline: "Kjører lokalt i nettleseren",
  },
  video: {
    title: "Filmen",
    lede:
      "Hvordan nettverket virker, fra én piksel til ferdig trent modell. Hver animasjon er skrevet i Manim, og hvert tall som vises på skjermen er hentet fra den samme treningskjøringen som driver demoen over.",
    play: "Spill av filmen",
    missing:
      "Filmen er ikke publisert ennå.",
    chapters: "Kapitler",
  },
  how: {
    title: "Hvordan det virker",
    lede:
      "Hele nettverket er to matrisemultiplikasjoner og en sigmoid. Det er ingen skjult kompleksitet — alt annet er trening.",
    steps: [
      {
        title: "Bildet blir en liste",
        body:
          "28×28 piksler brettes ut til én kolonne med 784 tall, hver delt på 255 så de ligger mellom 0 og 1. Den skaleringen er ikke pynt: uten den blir summene inn i sigmoid så store at den flater ut og gradientene forsvinner.",
      },
      {
        title: "784 → 128",
        body:
          "Hvert av de 128 skjulte nevronene ser på alle 784 pikslene, ganger hver med sin egen vekt, legger sammen og legger til et bias. Resultatet presses gjennom sigmoid til noe mellom 0 og 1. Det er 100 352 vekter i dette ene steget.",
      },
      {
        title: "128 → 10",
        body:
          "Samme operasjon en gang til, ned til ti tall — ett per siffer. Den høyeste vinner. Ingen softmax: nettverket er trent til å presse riktig utgang mot 1 og de andre mot 0, hver for seg.",
      },
      {
        title: "Og så bakover",
        body:
          "Feilen deriveres bakover gjennom begge lagene med kjerneregelen, og alle 101 770 parametrene flyttes et lite steg i retningen som gjør feilen mindre. Ti epoker, 32 bilder om gangen, 18 750 slike steg.",
      },
    ],
    codeCaption: "Hele forward-passet, slik det står i nn/network.py:",
    arch: { pixels: "piksler", hidden: "skjulte nevroner", digits: "siffer", weights: "vekter" },
  },
  gradcheck: {
    title: "Men var backprop riktig?",
    lede:
      "Dette er spørsmålet et ML-bibliotek svarer på for deg. Når man deriverer for hånd, må man svare selv — og en backprop med fortegnsfeil trener fortsatt, bare litt dårligere, så feilen kan gjemme seg lenge.",
    caption:
      "Testen: flytt én enkelt vekt et bittelite steg opp og ned, mål hvordan tapet faktisk endrer seg, og sammenlign med det backprop påstod. Fem tilfeldige vekter, begge lag.",
    takeaway:
      "Sifrene stemmer til ellevte desimal. Det er ikke «omtrent riktig» — det er så nær som flyttall kommer, og det betyr at derivasjonen er korrekt.",
  },
  training: {
    title: "Treningen",
    lede:
      "Ti epoker over 60 000 bilder. Den første epoken gjør nesten hele jobben; de ni neste henter inn de siste fire prosentpoengene.",
    axisEpoch: "Epoke",
    axisAcc: "Treffsikkerhet",
    axisLoss: "Tap",
    batchCaption:
      "Tapet per batch gjennom hele treningen — 18 750 steg, vist som median i vinduer. Støyen er ekte: hver batch er 32 tilfeldige bilder, og noen batcher er vanskeligere enn andre.",
    epochCaption: "Treffsikkerhet på testsettet etter hver epoke.",
  },
  learned: {
    title: "Hva den lærte",
    lede:
      "Hvert skjult nevron har 784 vekter — én per piksel. Bretter man dem tilbake til 28×28, ser man hva nevronet leter etter. Her er de tolv med sterkest utslag.",
    caption:
      "Grønt betyr «jeg vil ha lys her», oransje betyr «jeg vil ha mørkt her». De fleste ser ut som strukturert støy, ikke som pene strekdetektorer — og det er det ærlige svaret på hva et lite nettverk faktisk lærer.",
    legend: ["vil ha mørkt", "vil ha lys"],
  },
  misses: {
    title: "Hva den bommer på",
    lede:
      "De 20 bildene nettverket tok mest selvsikkert feil på. Sortert etter hvor sikkert det var — de øverste er de ubehagelige, for der er modellen skråsikker og feil på én gang.",
    said: "Gjettet",
    was: "Fasit",
    sure: "sikker",
    confusionTitle: "Alle bommene, sortert",
    confusionLede:
      "Dette er ikke en vanlig konfusjonsmatrise: den teller bare de 253 bildene av 10 000 som ble feilklassifisert, så diagonalen er tom med vilje. Raden er hva sifferet var, kolonnen er hva nettverket sa. Mønsteret er ikke tilfeldig — det er sifrene som faktisk ligner på hverandre når de er håndskrevet.",
    confusionRow: "Fasit",
    confusionCol: "Gjettet",
    confusionEmpty: "tom diagonal: treff telles ikke her",
    topTitle: "Vanligste forvekslinger",
    times: "ganger",
  },
  honest: {
    title: "Hva jeg ville gjort annerledes",
    body: [
      "Sigmoid i det siste laget med kvadratfeil er ikke det man ville valgt i dag. Softmax med kryssentropi gir gradienter som ikke forsvinner når nettverket er veldig sikkert og veldig feil, og ville trolig trent raskere til et bedre resultat. Jeg valgte sigmoid fordi det var den jeg kunne derivere for hånd og forstå fullt ut, og det var poenget med prosjektet.",
      "ReLU i det skjulte laget ville løst det samme problemet der. Med sigmoid i begge lag kryper gradienten sammen på vei bakover, og det er en stor del av grunnen til at læringsraten måtte helt opp i 1,0 for å komme noen vei.",
      "97,47 % er et godt resultat for et fullt tilkoblet nettverk på MNIST, men det er også taket for arkitekturen. Et konvolusjonsnettverk kommer over 99 % fordi det vet at nabopiksler hører sammen — informasjon som forsvinner i det øyeblikket jeg bretter bildet ut til en liste på 784 tall.",
    ],
  },
  footer: {
    built: "Bygget av Eivind Geiran",
    source: "All koden ligger åpent på GitHub",
    back: "Tilbake til eivindgeiran.no",
    colophon:
      "Nettverket er trent i NumPy, filmen er animert i Manim, og siden er Next.js. Alle tall på denne siden er hentet direkte fra treningskjøringen i artifacts/run.npz.",
  },
};

const en: Copy = {
  meta: {
    title: "A neural network from scratch — Eivind Geiran",
    description:
      "784 → 128 → 10, written in plain NumPy with no ML library. Draw a digit and run the real trained weights in your browser, and watch the film on how it works.",
  },
  nav: { repo: "Code", site: "eivindgeiran.no", video: "Film", demo: "Try it" },
  hero: {
    eyebrow: "MNIST · NumPy · Manim",
    title: "I built a neural network from scratch.",
    lede:
      "No TensorFlow, no PyTorch, no scikit-learn — just NumPy for the matrix math. Backpropagation is derived by hand and verified against numerical gradients. Then I made a film explaining how it works, animated in Manim. The network below is not a picture of a demo: those are the real weights, running in your browser.",
    stats: [
      { value: "97.47%", label: "accuracy on the test set" },
      { value: "101,770", label: "parameters" },
      { value: "0", label: "ML libraries used" },
      { value: "1.0e−11", label: "gradient check deviation" },
    ],
  },
  demo: {
    title: "Draw a digit",
    lede:
      "Use your mouse or finger. The network computes as you draw. Nothing is sent anywhere — the 101,770 parameters download once (199 KB) and the entire computation happens on your own machine.",
    clear: "Clear",
    examples: "Or try a real MNIST digit:",
    examplesHint: "These come from the training batch stored in run.npz.",
    drawHint: "Draw here",
    empty: "Draw a digit and it starts computing.",
    loading: "Loading weights …",
    error: "Could not load the weights. Try reloading the page.",
    verdict: "The network says",
    activation: "Output activation",
    hidden: "The hidden layer",
    hiddenNote:
      "128 neurons. Each square is one of them, and its brightness is how strongly it is firing right now. This is everything the network knows about your digit before it decides.",
    preprocessed: "What the network sees",
    preprocessNote:
      "Your drawing is cropped, scaled to 20×20 and centred by centre of mass in a 28×28 field — exactly how the MNIST images were normalised. Skip this step and the network misses systematically, and it is the preprocessing that is wrong, not the model.",
    notProbabilities:
      "Note: the outputs do not sum to 1. The network uses sigmoid and squared error, not softmax and cross-entropy, so each output is an independent answer between 0 and 1. That was a deliberate choice — more on it at the bottom.",
    offline: "Running locally in your browser",
  },
  video: {
    title: "The film",
    lede:
      "How the network works, from a single pixel to a trained model. Every animation is written in Manim, and every number on screen comes from the same training run that powers the demo above.",
    play: "Play the film",
    missing:
      "The film is not published yet.",
    chapters: "Chapters",
  },
  how: {
    title: "How it works",
    lede:
      "The whole network is two matrix multiplications and a sigmoid. There is no hidden complexity — everything else is training.",
    steps: [
      {
        title: "The image becomes a list",
        body:
          "28×28 pixels unroll into a single column of 784 numbers, each divided by 255 so they sit between 0 and 1. That scaling is not cosmetic: without it the sums going into the sigmoid get large enough that it flattens out and the gradients vanish.",
      },
      {
        title: "784 → 128",
        body:
          "Each of the 128 hidden neurons looks at all 784 pixels, multiplies each by its own weight, adds them up and adds a bias. The result is squashed through a sigmoid into something between 0 and 1. That single step holds 100,352 weights.",
      },
      {
        title: "128 → 10",
        body:
          "The same operation again, down to ten numbers — one per digit. The highest one wins. No softmax: the network is trained to push the correct output towards 1 and the others towards 0, independently.",
      },
      {
        title: "And then backwards",
        body:
          "The error is differentiated backwards through both layers with the chain rule, and all 101,770 parameters move one small step in the direction that shrinks it. Ten epochs, 32 images at a time, 18,750 such steps.",
      },
    ],
    codeCaption: "The entire forward pass, as it stands in nn/network.py:",
    arch: { pixels: "pixels", hidden: "hidden neurons", digits: "digits", weights: "weights" },
  },
  gradcheck: {
    title: "But was the backprop correct?",
    lede:
      "This is the question an ML library answers for you. Derive it by hand and you have to answer it yourself — and a backprop with a sign error still trains, just slightly worse, so the bug can hide for a long time.",
    caption:
      "The test: nudge a single weight a tiny step up and down, measure how the loss actually changes, and compare against what backprop claimed. Five random weights, both layers.",
    takeaway:
      "The digits agree to the eleventh decimal. That is not «roughly right» — it is as close as floating point gets, and it means the derivation is correct.",
  },
  training: {
    title: "The training",
    lede:
      "Ten epochs over 60,000 images. The first epoch does almost all the work; the remaining nine collect the last four percentage points.",
    axisEpoch: "Epoch",
    axisAcc: "Accuracy",
    axisLoss: "Loss",
    batchCaption:
      "Loss per batch across the whole run — 18,750 steps, shown as a windowed median. The noise is real: each batch is 32 random images, and some batches are harder than others.",
    epochCaption: "Test-set accuracy after each epoch.",
  },
  learned: {
    title: "What it learned",
    lede:
      "Each hidden neuron has 784 weights — one per pixel. Fold them back into 28×28 and you see what that neuron is looking for. Here are the twelve with the strongest response.",
    caption:
      "Green means «I want brightness here», orange means «I want darkness here». Most look like structured noise rather than tidy stroke detectors — and that is the honest answer to what a small network actually learns.",
    legend: ["wants dark", "wants bright"],
  },
  misses: {
    title: "What it gets wrong",
    lede:
      "The 20 images the network was most confidently wrong about. Sorted by how sure it was — the top ones are the uncomfortable ones, because there the model is certain and mistaken at the same time.",
    said: "Guessed",
    was: "Truth",
    sure: "sure",
    confusionTitle: "Every miss, sorted",
    confusionLede:
      "This is not an ordinary confusion matrix: it counts only the 253 images out of 10,000 that were misclassified, so the diagonal is deliberately empty. The row is what the digit was, the column is what the network said. The pattern is not random — these are the digits that genuinely resemble each other in handwriting.",
    confusionRow: "Truth",
    confusionCol: "Guessed",
    confusionEmpty: "empty diagonal: hits are not counted here",
    topTitle: "Most common confusions",
    times: "times",
  },
  honest: {
    title: "What I would do differently",
    body: [
      "A sigmoid output layer with squared error is not what you would pick today. Softmax with cross-entropy gives gradients that do not vanish when the network is very confident and very wrong, and would likely have trained faster to a better result. I chose sigmoid because it was the one I could differentiate by hand and understand completely, and that was the point of the project.",
      "ReLU in the hidden layer would have solved the same problem there. With sigmoid in both layers the gradient shrinks on its way backwards, and that is a large part of why the learning rate had to go all the way up to 1.0 to get anywhere.",
      "97.47% is a good result for a fully connected network on MNIST, but it is also the ceiling for this architecture. A convolutional network gets past 99% because it knows that neighbouring pixels belong together — information that disappears the moment I unroll the image into a list of 784 numbers.",
    ],
  },
  footer: {
    built: "Built by Eivind Geiran",
    source: "All the code is open on GitHub",
    back: "Back to eivindgeiran.no",
    colophon:
      "The network is trained in NumPy, the film is animated in Manim, and this page is Next.js. Every number here comes straight from the training run in artifacts/run.npz.",
  },
};

export const COPY: Record<Lang, Copy> = { no, en };
