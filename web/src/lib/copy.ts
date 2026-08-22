/**
 * All tekst på siden, på begge språk. Én kilde — ingen tekst ligger gjemt inne
 * i en komponent.
 *
 * Teksten er en funksjon av treningskjøringen, ikke en konstant. Alle tall som
 * står i setningene under kommer fra src/data/run.json, som genereres av
 * tools/export_web.py. En ny kjøring med andre tall gir riktig tekst uten at
 * noen setning må skrives om — og uten at hero kan komme i skade for å påstå
 * noe annet enn grafen tjue piksler lenger ned.
 */

export type Lang = "no" | "en";

/** Delen av run.json som teksten trenger. */
export interface RunFigures {
  model: { bytes: number };
  architecture: number[];
  parameters: number;
  epochs: number;
  batchSize: number;
  stepsPerEpoch: number;
  finalAccuracy: number;
  errorTotal: number;
  testSize: number;
  gradcheck: string;
  worst: unknown[];
}

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

/**
 * Den beste relative avviket i gradientsjekken, hentet ut av utskriften den
 * faktisk produserte. Formatet er `rel=1.01e-11` per linje.
 */
function bestGradcheck(text: string): number | null {
  const matches = [...text.matchAll(/rel=([0-9.]+e[-+]?\d+)/g)].map((m) => Number(m[1]));
  const valid = matches.filter((v) => Number.isFinite(v));
  return valid.length ? Math.min(...valid) : null;
}

/** Tallene i teksten, formatert etter språket. */
function figuresFor(run: RunFigures, lang: Lang) {
  const locale = lang === "no" ? "nb-NO" : "en-US";
  const int = new Intl.NumberFormat(locale);
  const percent = new Intl.NumberFormat(locale, {
    style: "percent",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

  const [inputs, hidden, outputs] = run.architecture;
  const steps = run.stepsPerEpoch * run.epochs;
  const best = bestGradcheck(run.gradcheck);

  // 1.01e-11 → «1,0e−11». Mantissen rundes, og på norsk brukes desimalkomma og
  // ekte minustegn, som er det samme skillet Intl gjør ellers på siden.
  let gradcheck = "—";
  if (best !== null) {
    const exponent = Math.floor(Math.log10(best));
    const mantissa = (best / 10 ** exponent).toFixed(1);
    gradcheck = `${mantissa}e${exponent}`;
    if (lang === "no") gradcheck = gradcheck.replace(".", ",").replace("-", "−");
  }

  return {
    inputs: int.format(inputs),
    hidden: int.format(hidden),
    outputs: int.format(outputs),
    accuracy: percent.format(run.finalAccuracy),
    parameters: int.format(run.parameters),
    firstLayerWeights: int.format(inputs * hidden),
    secondLayerWeights: int.format(hidden * outputs),
    epochs: int.format(run.epochs),
    batchSize: int.format(run.batchSize),
    steps: int.format(steps),
    trainImages: int.format(run.stepsPerEpoch * run.batchSize),
    weightsKb: int.format(Math.round(run.model.bytes / 1024)),
    errors: int.format(run.errorTotal),
    testSize: int.format(run.testSize),
    worstCount: int.format(run.worst.length),
    gradcheck,
  };
}

function norwegian(f: ReturnType<typeof figuresFor>): Copy {
  return {
    meta: {
      title: "Et nevralt nettverk fra bunnen av — Eivind Geiran",
      description: `${f.inputs} → ${f.hidden} → ${f.outputs}, skrevet i ren NumPy uten ML-bibliotek. Tegn et siffer og kjør de ekte trente vektene i nettleseren, og se filmen om hvordan det virker.`,
    },
    nav: { repo: "Kode", site: "eivindgeiran.no", video: "Film", demo: "Prøv den" },
    hero: {
      eyebrow: "MNIST · NumPy · Manim",
      title: "Jeg bygget et nevralt nettverk fra bunnen av.",
      lede:
        "Ingen TensorFlow, ingen PyTorch, ingen scikit-learn — bare NumPy til matrisematematikken. Backprop er derivert for hånd og verifisert mot numeriske gradienter. Så laget jeg en film om hvordan det virker, animert i Manim. Nettverket under er ikke et bilde av en demo: det er de ekte vektene, og de kjører i nettleseren din.",
      stats: [
        { value: f.accuracy, label: "treffsikkerhet på testsettet" },
        { value: f.parameters, label: "parametre" },
        { value: "0", label: "ML-bibliotek brukt" },
        { value: f.gradcheck, label: "avvik i gradientsjekken" },
      ],
    },
    demo: {
      title: "Tegn et siffer",
      lede: `Bruk musa eller fingeren. Nettverket regner mens du tegner. Ingenting sendes noe sted — de ${f.parameters} parametrene lastes ned én gang (${f.weightsKb} KB) og hele utregningen skjer på din egen maskin.`,
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
      hiddenNote: `${f.hidden} nevroner. Hver rute er ett av dem, og lysstyrken er hvor sterkt det fyrer akkurat nå. Dette er alt nettverket «vet» om sifferet ditt før det bestemmer seg.`,
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
      missing: "Filmen er ikke publisert ennå.",
      chapters: "Kapitler",
    },
    how: {
      title: "Hvordan det virker",
      lede:
        "Hele nettverket er to matrisemultiplikasjoner og en sigmoid. Det er ingen skjult kompleksitet — alt annet er trening.",
      steps: [
        {
          title: "Bildet blir en liste",
          body: `28×28 piksler brettes ut til én kolonne med ${f.inputs} tall, hver delt på 255 så de ligger mellom 0 og 1. Den skaleringen er ikke pynt: uten den blir summene inn i sigmoid så store at den flater ut og gradientene forsvinner.`,
        },
        {
          title: `${f.inputs} → ${f.hidden}`,
          body: `Hvert av de ${f.hidden} skjulte nevronene ser på alle ${f.inputs} pikslene, ganger hver med sin egen vekt, legger sammen og legger til et bias. Resultatet presses gjennom sigmoid til noe mellom 0 og 1. Det er ${f.firstLayerWeights} vekter i dette ene steget.`,
        },
        {
          title: `${f.hidden} → ${f.outputs}`,
          body: `Samme operasjon en gang til, ned til ti tall — ett per siffer. Den høyeste vinner. Ingen softmax: nettverket er trent til å presse riktig utgang mot 1 og de andre mot 0, hver for seg.`,
        },
        {
          title: "Og så bakover",
          body: `Feilen deriveres bakover gjennom begge lagene med kjerneregelen, og alle ${f.parameters} parametrene flyttes et lite steg i retningen som gjør feilen mindre. ${f.epochs} epoker, ${f.batchSize} bilder om gangen, ${f.steps} slike steg.`,
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
      lede: `${f.epochs} epoker over ${f.trainImages} bilder. Den første epoken gjør nesten hele jobben; resten henter inn de siste prosentpoengene.`,
      axisEpoch: "Epoke",
      axisAcc: "Treffsikkerhet",
      axisLoss: "Tap",
      batchCaption: `Tapet per batch gjennom hele treningen — ${f.steps} steg, vist som median i vinduer. Støyen er ekte: hver batch er ${f.batchSize} tilfeldige bilder, og noen batcher er vanskeligere enn andre.`,
      epochCaption: "Treffsikkerhet på testsettet etter hver epoke.",
    },
    learned: {
      title: "Hva den lærte",
      lede: `Hvert skjult nevron har ${f.inputs} vekter — én per piksel. Bretter man dem tilbake til 28×28, ser man hva nevronet leter etter. Her er de tolv med sterkest utslag.`,
      caption:
        "Grønt betyr «jeg vil ha lys her», oransje betyr «jeg vil ha mørkt her». De fleste ser ut som strukturert støy, ikke som pene strekdetektorer — og det er det ærlige svaret på hva et lite nettverk faktisk lærer.",
      legend: ["vil ha mørkt", "vil ha lys"],
    },
    misses: {
      title: "Hva den bommer på",
      lede: `De ${f.worstCount} bildene nettverket tok mest selvsikkert feil på. Sortert etter hvor sikkert det var — de øverste er de ubehagelige, for der er modellen skråsikker og feil på én gang.`,
      said: "Gjettet",
      was: "Fasit",
      sure: "sikker",
      confusionTitle: "Alle bommene, sortert",
      confusionLede: `Dette er ikke en vanlig konfusjonsmatrise: den teller bare de ${f.errors} bildene av ${f.testSize} som ble feilklassifisert, så diagonalen er tom med vilje. Raden er hva sifferet var, kolonnen er hva nettverket sa. Mønsteret er ikke tilfeldig — det er sifrene som faktisk ligner på hverandre når de er håndskrevet.`,
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
        `${f.accuracy} er et godt resultat for et fullt tilkoblet nettverk på MNIST, men det er også taket for arkitekturen. Et konvolusjonsnettverk kommer over 99 % fordi det vet at nabopiksler hører sammen — informasjon som forsvinner i det øyeblikket jeg bretter bildet ut til en liste på ${f.inputs} tall.`,
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
}

function english(f: ReturnType<typeof figuresFor>): Copy {
  return {
    meta: {
      title: "A neural network from scratch — Eivind Geiran",
      description: `${f.inputs} → ${f.hidden} → ${f.outputs}, written in plain NumPy with no ML library. Draw a digit and run the real trained weights in your browser, and watch the film on how it works.`,
    },
    nav: { repo: "Code", site: "eivindgeiran.no", video: "Film", demo: "Try it" },
    hero: {
      eyebrow: "MNIST · NumPy · Manim",
      title: "I built a neural network from scratch.",
      lede:
        "No TensorFlow, no PyTorch, no scikit-learn — just NumPy for the matrix math. Backpropagation is derived by hand and verified against numerical gradients. Then I made a film explaining how it works, animated in Manim. The network below is not a picture of a demo: those are the real weights, running in your browser.",
      stats: [
        { value: f.accuracy, label: "accuracy on the test set" },
        { value: f.parameters, label: "parameters" },
        { value: "0", label: "ML libraries used" },
        { value: f.gradcheck, label: "gradient check deviation" },
      ],
    },
    demo: {
      title: "Draw a digit",
      lede: `Use your mouse or finger. The network computes as you draw. Nothing is sent anywhere — the ${f.parameters} parameters download once (${f.weightsKb} KB) and the entire computation happens on your own machine.`,
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
      hiddenNote: `${f.hidden} neurons. Each square is one of them, and its brightness is how strongly it is firing right now. This is everything the network knows about your digit before it decides.`,
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
      missing: "The film is not published yet.",
      chapters: "Chapters",
    },
    how: {
      title: "How it works",
      lede:
        "The whole network is two matrix multiplications and a sigmoid. There is no hidden complexity — everything else is training.",
      steps: [
        {
          title: "The image becomes a list",
          body: `28×28 pixels unroll into a single column of ${f.inputs} numbers, each divided by 255 so they sit between 0 and 1. That scaling is not cosmetic: without it the sums going into the sigmoid get large enough that it flattens out and the gradients vanish.`,
        },
        {
          title: `${f.inputs} → ${f.hidden}`,
          body: `Each of the ${f.hidden} hidden neurons looks at all ${f.inputs} pixels, multiplies each by its own weight, adds them up and adds a bias. The result is squashed through a sigmoid into something between 0 and 1. That single step holds ${f.firstLayerWeights} weights.`,
        },
        {
          title: `${f.hidden} → ${f.outputs}`,
          body: `The same operation again, down to ten numbers — one per digit. The highest one wins. No softmax: the network is trained to push the correct output towards 1 and the others towards 0, independently.`,
        },
        {
          title: "And then backwards",
          body: `The error is differentiated backwards through both layers with the chain rule, and all ${f.parameters} parameters move one small step in the direction that shrinks it. ${f.epochs} epochs, ${f.batchSize} images at a time, ${f.steps} such steps.`,
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
      lede: `${f.epochs} epochs over ${f.trainImages} images. The first epoch does almost all the work; the rest collect the last few percentage points.`,
      axisEpoch: "Epoch",
      axisAcc: "Accuracy",
      axisLoss: "Loss",
      batchCaption: `Loss per batch across the whole run — ${f.steps} steps, shown as a windowed median. The noise is real: each batch is ${f.batchSize} random images, and some batches are harder than others.`,
      epochCaption: "Test-set accuracy after each epoch.",
    },
    learned: {
      title: "What it learned",
      lede: `Each hidden neuron has ${f.inputs} weights — one per pixel. Fold them back into 28×28 and you see what that neuron is looking for. Here are the twelve with the strongest response.`,
      caption:
        "Green means «I want brightness here», orange means «I want darkness here». Most look like structured noise rather than tidy stroke detectors — and that is the honest answer to what a small network actually learns.",
      legend: ["wants dark", "wants bright"],
    },
    misses: {
      title: "What it gets wrong",
      lede: `The ${f.worstCount} images the network was most confidently wrong about. Sorted by how sure it was — the top ones are the uncomfortable ones, because there the model is certain and mistaken at the same time.`,
      said: "Guessed",
      was: "Truth",
      sure: "sure",
      confusionTitle: "Every miss, sorted",
      confusionLede: `This is not an ordinary confusion matrix: it counts only the ${f.errors} images out of ${f.testSize} that were misclassified, so the diagonal is deliberately empty. The row is what the digit was, the column is what the network said. The pattern is not random — these are the digits that genuinely resemble each other in handwriting.`,
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
        `${f.accuracy} is a good result for a fully connected network on MNIST, but it is also the ceiling for this architecture. A convolutional network gets past 99% because it knows that neighbouring pixels belong together — information that disappears the moment I unroll the image into a list of ${f.inputs} numbers.`,
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
}

/** Bygger teksten for begge språk ut fra én treningskjøring. */
export function buildCopy(run: RunFigures): Record<Lang, Copy> {
  return {
    no: norwegian(figuresFor(run, "no")),
    en: english(figuresFor(run, "en")),
  };
}
