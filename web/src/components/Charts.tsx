"use client";

import type { Copy, Lang } from "@/lib/copy";

/**
 * To diagrammer, tegnet som ren SVG. Ingen diagrambibliotek — det ville vært
 * mer kode enn dette, og siden skal laste raskt.
 */

type Props = {
  copy: Copy;
  lang: Lang;
  lossCurve: number[];
  epochAccuracy: number[];
  totalSteps: number;
};

const W = 520;
const H = 240;
const PAD_L = 44;
const PAD_B = 30;
const PAD_T = 12;
const PAD_R = 8;

export function LossChart({
  copy,
  lang,
  lossCurve,
  totalSteps,
}: {
  copy: Copy;
  lang: Lang;
  lossCurve: number[];
  totalSteps: number;
}) {
  const max = Math.max(...lossCurve);
  const x = (i: number) => PAD_L + (i / (lossCurve.length - 1)) * (W - PAD_L - PAD_R);
  const y = (v: number) => PAD_T + (1 - v / max) * (H - PAD_T - PAD_B);

  const path = lossCurve.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("");
  const ticks = [0, max / 2, max];

  return (
    <figure className="card" style={{ margin: 0 }}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={copy.training.batchCaption}>
        {ticks.map((t) => (
          <g key={t}>
            <line
              x1={PAD_L}
              x2={W - PAD_R}
              y1={y(t)}
              y2={y(t)}
              stroke="#232830"
              strokeWidth="1"
            />
            <text x={PAD_L - 8} y={y(t) + 3.5} textAnchor="end" fontSize="10" fill="#5c6675">
              {t.toFixed(1)}
            </text>
          </g>
        ))}
        <path d={path} fill="none" stroke="#d9ff63" strokeWidth="1.4" strokeLinejoin="round" />
        <text x={PAD_L} y={H - 8} fontSize="10" fill="#5c6675">
          0
        </text>
        <text x={W - PAD_R} y={H - 8} fontSize="10" fill="#5c6675" textAnchor="end">
          {new Intl.NumberFormat(lang === "no" ? "nb-NO" : "en-US").format(totalSteps)}
        </text>
        <text
          x={12}
          y={(H - PAD_B) / 2}
          fontSize="10"
          fill="#8b93a0"
          textAnchor="middle"
          transform={`rotate(-90 12 ${(H - PAD_B) / 2})`}
        >
          {copy.training.axisLoss}
        </text>
      </svg>
      <figcaption className="caption">{copy.training.batchCaption}</figcaption>
    </figure>
  );
}

export function AccuracyChart({
  copy,
  epochAccuracy,
}: {
  copy: Copy;
  epochAccuracy: number[];
}) {
  // Skalaen starter litt under første epoke i stedet for på null, ellers blir
  // hele kurven en flat strek helt oppe i taket og forskjellene forsvinner.
  const lo = Math.min(...epochAccuracy) - 0.005;
  const hi = 1.0;
  const x = (i: number) =>
    PAD_L + (i / (epochAccuracy.length - 1)) * (W - PAD_L - PAD_R);
  const y = (v: number) => PAD_T + (1 - (v - lo) / (hi - lo)) * (H - PAD_T - PAD_B);

  const path = epochAccuracy
    .map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`)
    .join("");

  // Faste trinn ville gitt en akse uten etiketter hvis treffsikkerheten lå
  // under det laveste av dem. Vi legger dem i stedet jevnt over det området
  // kurven faktisk bruker.
  const ticks = [0, 1, 2, 3].map((i) => lo + ((hi - lo) * i) / 3);

  return (
    <figure className="card" style={{ margin: 0 }}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={copy.training.epochCaption}>
        {ticks.map((t) => (
          <g key={t}>
            <line x1={PAD_L} x2={W - PAD_R} y1={y(t)} y2={y(t)} stroke="#232830" />
            <text x={PAD_L - 8} y={y(t) + 3.5} textAnchor="end" fontSize="10" fill="#5c6675">
              {(t * 100).toFixed(1)}%
            </text>
          </g>
        ))}
        <path d={path} fill="none" stroke="#d9ff63" strokeWidth="2" strokeLinejoin="round" />
        {epochAccuracy.map((v, i) => (
          <g key={i}>
            <circle cx={x(i)} cy={y(v)} r="3.2" fill="#0c0e11" stroke="#d9ff63" strokeWidth="1.6" />
            {i === epochAccuracy.length - 1 ? (
              <text x={x(i)} y={y(v) - 12} fontSize="11" fill="#d9ff63" textAnchor="end">
                {(v * 100).toFixed(2)}%
              </text>
            ) : null}
          </g>
        ))}
        {epochAccuracy.map((_, i) =>
          i % 2 === 0 ? (
            <text key={i} x={x(i)} y={H - 8} fontSize="10" fill="#5c6675" textAnchor="middle">
              {i + 1}
            </text>
          ) : null,
        )}
        <text
          x={12}
          y={(H - PAD_B) / 2}
          fontSize="10"
          fill="#8b93a0"
          textAnchor="middle"
          transform={`rotate(-90 12 ${(H - PAD_B) / 2})`}
        >
          {copy.training.axisAcc}
        </text>
      </svg>
      <figcaption className="caption">{copy.training.epochCaption}</figcaption>
    </figure>
  );
}

export default function Charts({
  copy,
  lang,
  lossCurve,
  epochAccuracy,
  totalSteps,
}: Props) {
  return (
    <div className="chartRow">
      <LossChart copy={copy} lang={lang} lossCurve={lossCurve} totalSteps={totalSteps} />
      <AccuracyChart copy={copy} epochAccuracy={epochAccuracy} />
    </div>
  );
}
