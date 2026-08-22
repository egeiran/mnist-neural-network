"use client";

import { useEffect, useRef } from "react";
import type { Copy } from "@/lib/copy";
import { decodeDigit } from "@/lib/model";
import { drawDigit, drawWeights } from "@/lib/render";
import { MNIST_SIZE } from "@/lib/preprocess";

type Miss = { index: number; true: number; pred: number; confidence: number };

function DigitCanvas({ b64 }: { b64: string }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (ref.current) drawDigit(ref.current, decodeDigit(b64));
  }, [b64]);
  return <canvas ref={ref} width={MNIST_SIZE} height={MNIST_SIZE} />;
}

export function Misses({
  copy,
  worst,
  images,
}: {
  copy: Copy;
  worst: Miss[];
  images: string[];
}) {
  return (
    <div className="missGrid">
      {worst.map((miss, i) => (
        <figure className="miss" key={miss.index} style={{ margin: 0 }}>
          <DigitCanvas b64={images[i]} />
          <figcaption className="missBody">
            <span className="missLine">
              {copy.misses.said} <span className="missSaid">{miss.pred}</span>
            </span>
            <span className="missLine">
              {copy.misses.was} <span className="missWas">{miss.true}</span>
            </span>
            <span className="missConf">
              {(miss.confidence * 100).toFixed(1)} % {copy.misses.sure}
            </span>
          </figcaption>
        </figure>
      ))}
    </div>
  );
}

export function Confusion({
  copy,
  matrix,
  top,
}: {
  copy: Copy;
  matrix: number[][];
  top: { true: number; pred: number; count: number }[];
}) {
  // Matrisen i run.npz teller bare feilklassifiseringene, så diagonalen er
  // null ved konstruksjon. Vi tegner den som strukturelt tom i stedet for å
  // late som den inneholder treffene.
  let maxOff = 1;
  matrix.forEach((row, i) =>
    row.forEach((v, j) => {
      if (i !== j && v > maxOff) maxOff = v;
    }),
  );

  return (
    <>
      <div className="matrix" role="table" aria-label={copy.misses.confusionTitle}>
      <span className="matrixHead" />
      {Array.from({ length: 10 }, (_, j) => (
        <span className="matrixHead" key={`h${j}`}>
          {j}
        </span>
      ))}

      {matrix.map((row, i) => (
        <Row key={i} i={i} row={row} maxOff={maxOff} />
      ))}
      </div>

      <p className="caption">
        {copy.misses.confusionRow} ↓ · {copy.misses.confusionCol} → ·{" "}
        {copy.misses.confusionEmpty}
      </p>

      <p className="subhead">{copy.misses.topTitle}</p>
      <div className="topMiss">
        {top.map((t) => (
          <span className="chip" key={`${t.true}-${t.pred}`}>
            <b>{t.true}</b> → <i>{t.pred}</i>
            <em>
              {t.count} {copy.misses.times}
            </em>
          </span>
        ))}
      </div>
    </>
  );
}

function Row({ i, row, maxOff }: { i: number; row: number[]; maxOff: number }) {
  return (
    <>
      <span className="matrixHead">{i}</span>
      {row.map((v, j) => {
        const isDiag = i === j;
        const t = Math.min(v / maxOff, 1);
        return (
          <span
            className="cell"
            data-diag={isDiag}
            key={j}
            style={
              isDiag
                ? undefined
                : {
                    background:
                      v === 0 ? "#11141a" : `rgba(255, 143, 90, ${(0.2 + t * 0.8).toFixed(3)})`,
                    color: t > 0.45 ? "#0c0e11" : "#8b93a0",
                  }
            }
            title={isDiag ? undefined : `${i} → ${j}: ${v}`}
          >
            {isDiag ? "" : v || ""}
          </span>
        );
      })}
    </>
  );
}

export function Filters({
  copy,
  filters,
}: {
  copy: Copy;
  filters: { neuron: number; limit: number; w: number[] }[];
}) {
  return (
    <>
      <div className="filters">
        {filters.map((f) => (
          <FilterCard key={f.neuron} filter={f} />
        ))}
      </div>
      <div className="legend">
        <span>{copy.learned.legend[0]}</span>
        <span className="legendBar" />
        <span>{copy.learned.legend[1]}</span>
      </div>
      <p className="caption">{copy.learned.caption}</p>
    </>
  );
}

function FilterCard({ filter }: { filter: { neuron: number; limit: number; w: number[] } }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (ref.current) drawWeights(ref.current, filter.w, filter.limit);
  }, [filter]);

  return (
    <figure className="filter" style={{ margin: 0 }}>
      <canvas ref={ref} width={MNIST_SIZE} height={MNIST_SIZE} />
      <figcaption>#{filter.neuron}</figcaption>
    </figure>
  );
}
