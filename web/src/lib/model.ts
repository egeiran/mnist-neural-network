/**
 * Nettverket, kjørende i nettleseren.
 *
 * Vektene er de samme som ble trent i nn/train.py — 784 → 128 → 10, sigmoid i
 * begge lag, 101 770 parametre. De lastes ned som én float16-fil på 199 KB og
 * pakkes ut til Float32Array her. Det er ingen server involvert: alt under
 * kjører på maskinen til den som besøker siden.
 */

export type Layout = { name: string; shape: number[]; offset: number };

export type Manifest = {
  file: string;
  dtype: string;
  bytes: number;
  layout: Layout[];
};

export type Model = {
  W1: Float32Array; // 784 x 128, radvis
  b1: Float32Array; // 128
  W2: Float32Array; // 128 x 10, radvis
  b2: Float32Array; // 10
};

export type Prediction = {
  /** 10 utgangsaktiveringer i [0, 1]. Summerer seg IKKE til 1 — se noten under. */
  out: Float32Array;
  /** 128 skjulte aktiveringer i [0, 1]. */
  hidden: Float32Array;
  /** Indeksen til den høyeste utgangen. */
  digit: number;
};

/**
 * float16 → float32. Nettleserne har fått Float16Array, men ikke alle vi bryr
 * oss om, så vi pakker ut for hånd. Konverteringen er eksakt: hver float16 har
 * en float32 som treffer den presist.
 */
function decodeFloat16(bits: number): number {
  const sign = bits & 0x8000 ? -1 : 1;
  const exponent = (bits >> 10) & 0x1f;
  const fraction = bits & 0x03ff;

  if (exponent === 0) {
    // Subnormale tall (og null).
    return sign * 2 ** -14 * (fraction / 1024);
  }
  if (exponent === 0x1f) {
    return fraction === 0 ? sign * Infinity : NaN;
  }
  return sign * 2 ** (exponent - 15) * (1 + fraction / 1024);
}

function readSlice(view: DataView, offset: number, length: number): Float32Array {
  const out = new Float32Array(length);
  for (let i = 0; i < length; i++) {
    // true = little-endian, som er det export_web.py skriver.
    out[i] = decodeFloat16(view.getUint16((offset + i) * 2, true));
  }
  return out;
}

/** Deler opp den nedlastede fila i de fire matrisene. Skilt ut fra loadModel
 *  så den kan testes i Node uten nettverk — se tools/check_web_model.ts. */
export function decodeWeights(buffer: ArrayBuffer, manifest: Manifest): Model {
  const view = new DataView(buffer);

  const slot = (name: string): Float32Array => {
    const entry = manifest.layout.find((l) => l.name === name);
    if (!entry) throw new Error(`vektfila mangler ${name}`);
    const length = entry.shape.reduce((a, b) => a * b, 1);
    return readSlice(view, entry.offset, length);
  };

  return { W1: slot("W1"), b1: slot("b1"), W2: slot("W2"), b2: slot("b2") };
}

export async function loadModel(manifest: Manifest, signal?: AbortSignal): Promise<Model> {
  const response = await fetch(manifest.file, { signal });
  if (!response.ok) {
    throw new Error(`klarte ikke laste vektene (${response.status})`);
  }
  return decodeWeights(await response.arrayBuffer(), manifest);
}

function sigmoid(z: number): number {
  return 1 / (1 + Math.exp(-z));
}

/**
 * Forward pass. To matrisemultiplikasjoner og en sigmoid — det er hele
 * nettverket.
 *
 * Det ene trikset her: et tegnet siffer er for det meste svart, så vi hopper
 * over inngangene som er null. Da faller den tyngste løkka fra 100 352
 * multiplikasjoner til typisk 10–20 000, og demoen kan kjøre på hvert eneste
 * museklikk uten å henge.
 */
export function predict(model: Model, x: Float32Array): Prediction {
  const { W1, b1, W2, b2 } = model;
  const hidden = new Float32Array(128);

  hidden.set(b1);
  for (let i = 0; i < 784; i++) {
    const xi = x[i];
    if (xi === 0) continue;
    const row = i * 128;
    for (let j = 0; j < 128; j++) {
      hidden[j] += xi * W1[row + j];
    }
  }
  for (let j = 0; j < 128; j++) {
    hidden[j] = sigmoid(hidden[j]);
  }

  const out = new Float32Array(10);
  out.set(b2);
  for (let j = 0; j < 128; j++) {
    const hj = hidden[j];
    const row = j * 10;
    for (let k = 0; k < 10; k++) {
      out[k] += hj * W2[row + k];
    }
  }

  let digit = 0;
  for (let k = 0; k < 10; k++) {
    out[k] = sigmoid(out[k]);
    if (out[k] > out[digit]) digit = k;
  }

  return { out, hidden, digit };
}

/** Pakker ut et 28x28-bilde lagret som 784 base64-bytes. */
export function decodeDigit(b64: string): Float32Array {
  const binary = atob(b64);
  const out = new Float32Array(784);
  for (let i = 0; i < 784; i++) {
    out[i] = binary.charCodeAt(i) / 255;
  }
  return out;
}
