/** Små tegnehjelpere som flere komponenter deler. */

import { MNIST_SIZE } from "./preprocess";

/** Maler 784 gråtoneverdier inn i et 28x28-lerret. */
export function drawDigit(canvas: HTMLCanvasElement, digit: Float32Array): void {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const image = ctx.createImageData(MNIST_SIZE, MNIST_SIZE);
  for (let i = 0; i < digit.length; i++) {
    const v = Math.round(Math.min(Math.max(digit[i], 0), 1) * 255);
    image.data[i * 4] = v;
    image.data[i * 4 + 1] = v;
    image.data[i * 4 + 2] = v;
    image.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(image, 0, 0);
}

/**
 * Maler vektene til ett skjult nevron som et 28x28-bilde: oransje der nevronet
 * vil ha mørke piksler, limegrønt der det vil ha lyse. Skalaen er nevronets
 * egen største absoluttverdi, så hvert bilde bruker hele fargespennet.
 */
export function drawWeights(
  canvas: HTMLCanvasElement,
  weights: number[],
  limit: number,
): void {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const image = ctx.createImageData(MNIST_SIZE, MNIST_SIZE);

  for (let i = 0; i < weights.length; i++) {
    const t = limit > 0 ? Math.min(Math.max(weights[i] / limit, -1), 1) : 0;
    // Bakgrunnen er panelfargen; vi blander mot lime for positivt og oransje
    // for negativt, så et nevron uten mening blir mørkt i stedet for grått rot.
    const base = 17;
    const [r, g, b] =
      t >= 0
        ? [base + (217 - base) * t, base + (255 - base) * t, base + (99 - base) * t]
        : [base + (255 - base) * -t, base + (143 - base) * -t, base + (90 - base) * -t];

    image.data[i * 4] = r;
    image.data[i * 4 + 1] = g;
    image.data[i * 4 + 2] = b;
    image.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(image, 0, 0);
}
