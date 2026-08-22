/**
 * Sjekker at nettleserversjonen av nettverket gir samme svar som NumPy.
 *
 *   python tools/check_web_model.py > /tmp/expected.json
 *   node --experimental-strip-types tools/check_web_model.ts /tmp/expected.json
 *
 * Uten denne testen ville «demoen kjører de ekte vektene» vært en påstand.
 * Med den er det noe som er målt: samme 57 bilder gjennom begge, og avviket
 * skrives ut.
 */

import { readFileSync } from "node:fs";
import { decodeWeights, predict, decodeDigit, type Manifest } from "../web/src/lib/model.ts";

const expectedPath = process.argv[2];
if (!expectedPath) {
  console.error("bruk: node --experimental-strip-types tools/check_web_model.ts <expected.json>");
  process.exit(1);
}

const expected = JSON.parse(readFileSync(expectedPath, "utf8")) as {
  manifest: Manifest;
  images: string[];
  out: number[][];
};

const raw = readFileSync(new URL("../web/public" + expected.manifest.file, import.meta.url));
const buffer = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength) as ArrayBuffer;
const model = decodeWeights(buffer, expected.manifest);

let maxDiff = 0;
let disagreements = 0;

expected.images.forEach((b64, i) => {
  const { out, digit } = predict(model, decodeDigit(b64));
  const want = expected.out[i];

  let wantDigit = 0;
  for (let k = 0; k < 10; k++) if (want[k] > want[wantDigit]) wantDigit = k;
  if (wantDigit !== digit) disagreements++;

  for (let k = 0; k < 10; k++) {
    maxDiff = Math.max(maxDiff, Math.abs(out[k] - want[k]));
  }
});

console.log(`bilder sjekket:        ${expected.images.length}`);
console.log(`største avvik:         ${maxDiff.toExponential(2)}`);
console.log(`ulike prediksjoner:    ${disagreements}`);

if (disagreements > 0 || maxDiff > 1e-3) {
  console.error("\nJS og NumPy er ikke enige — ikke publiser dette.");
  process.exit(1);
}
console.log("\nOK: nettleseren regner det samme som NumPy.");
