/**
 * Fra tegneflate til noe nettverket kjenner igjen.
 *
 * Dette steget er lett å hoppe over, og da virker ikke demoen. MNIST-sifrene er
 * ikke fotografier av tall — de er normalisert på en helt bestemt måte, og et
 * nettverk trent på dem har aldri sett noe annet:
 *
 *   1. sifferet beskjæres til sin egen omsluttende boks
 *   2. boksen skaleres så den lengste siden blir 20 piksler (formen beholdes)
 *   3. resultatet legges i et 28x28-felt slik at TYNGDEPUNKTET havner i midten
 *
 * Punkt 3 er det som overrasker: MNIST sentrerer ikke etter boksen, men etter
 * massemidtpunktet. En firer med lang hale får derfor boksen forskjøvet oppover.
 * Gjør man dette feil, blir sjuere til toere og niere til firere, helt
 * systematisk.
 */

export const MNIST_SIZE = 28;
const BOX = 20; // sifferet skaleres inn i 20x20, med 4 px marg rundt

/** Henter gråtoneverdier 0–1 fra en kvadratisk tegneflate. */
function intensities(source: HTMLCanvasElement): { data: Float32Array; size: number } {
  const size = source.width;
  const ctx = source.getContext("2d", { willReadFrequently: true });
  if (!ctx) throw new Error("fikk ikke 2d-kontekst");
  const pixels = ctx.getImageData(0, 0, size, size).data;

  const data = new Float32Array(size * size);
  for (let i = 0; i < size * size; i++) {
    // Vi tegner hvitt på svart, som MNIST, så den røde kanalen er nok.
    data[i] = pixels[i * 4] / 255;
  }
  return { data, size };
}

type Box = { x0: number; y0: number; x1: number; y1: number };

function boundingBox(data: Float32Array, size: number): Box | null {
  let x0 = size;
  let y0 = size;
  let x1 = -1;
  let y1 = -1;

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      if (data[y * size + x] > 0.02) {
        if (x < x0) x0 = x;
        if (x > x1) x1 = x;
        if (y < y0) y0 = y;
        if (y > y1) y1 = y;
      }
    }
  }
  return x1 < 0 ? null : { x0, y0, x1, y1 };
}

/**
 * Nedskalering med boksfilter: hver målpiksel er gjennomsnittet av alle
 * kildepikslene den dekker. Det gir den samme mykheten som MNIST-bildene har,
 * i motsetning til nærmeste nabo, som lager hakkete streker nettverket aldri
 * har sett maken til.
 */
function resample(
  data: Float32Array,
  size: number,
  box: Box,
  outW: number,
  outH: number,
): Float32Array {
  const out = new Float32Array(outW * outH);
  const boxW = box.x1 - box.x0 + 1;
  const boxH = box.y1 - box.y0 + 1;

  for (let oy = 0; oy < outH; oy++) {
    const sy0 = box.y0 + (oy * boxH) / outH;
    const sy1 = box.y0 + ((oy + 1) * boxH) / outH;

    for (let ox = 0; ox < outW; ox++) {
      const sx0 = box.x0 + (ox * boxW) / outW;
      const sx1 = box.x0 + ((ox + 1) * boxW) / outW;

      let sum = 0;
      let weight = 0;
      for (let y = Math.floor(sy0); y < Math.min(Math.ceil(sy1), size); y++) {
        const wy = Math.min(y + 1, sy1) - Math.max(y, sy0);
        if (wy <= 0) continue;
        for (let x = Math.floor(sx0); x < Math.min(Math.ceil(sx1), size); x++) {
          const wx = Math.min(x + 1, sx1) - Math.max(x, sx0);
          if (wx <= 0) continue;
          sum += data[y * size + x] * wy * wx;
          weight += wy * wx;
        }
      }
      out[oy * outW + ox] = weight > 0 ? sum / weight : 0;
    }
  }
  return out;
}

/**
 * Hele kjeden. Returnerer 784 verdier i [0, 1], klare for predict(),
 * eller null hvis flaten er tom.
 */
export function canvasToMnist(source: HTMLCanvasElement): Float32Array | null {
  const { data, size } = intensities(source);
  const box = boundingBox(data, size);
  if (!box) return null;

  // Steg 2: lengste side blir 20 px, den andre skaleres i samme forhold.
  const boxW = box.x1 - box.x0 + 1;
  const boxH = box.y1 - box.y0 + 1;
  const scale = BOX / Math.max(boxW, boxH);
  const outW = Math.max(1, Math.round(boxW * scale));
  const outH = Math.max(1, Math.round(boxH * scale));
  const small = resample(data, size, box, outW, outH);

  // Steg 3: finn tyngdepunktet og legg det i midten av 28x28.
  let mass = 0;
  let cx = 0;
  let cy = 0;
  for (let y = 0; y < outH; y++) {
    for (let x = 0; x < outW; x++) {
      const v = small[y * outW + x];
      mass += v;
      cx += v * x;
      cy += v * y;
    }
  }
  if (mass === 0) return null;
  cx /= mass;
  cy /= mass;

  const offsetX = Math.round(MNIST_SIZE / 2 - cx);
  const offsetY = Math.round(MNIST_SIZE / 2 - cy);

  const out = new Float32Array(MNIST_SIZE * MNIST_SIZE);
  for (let y = 0; y < outH; y++) {
    const ty = y + offsetY;
    if (ty < 0 || ty >= MNIST_SIZE) continue;
    for (let x = 0; x < outW; x++) {
      const tx = x + offsetX;
      if (tx < 0 || tx >= MNIST_SIZE) continue;
      out[ty * MNIST_SIZE + tx] = small[y * outW + x];
    }
  }
  return out;
}
