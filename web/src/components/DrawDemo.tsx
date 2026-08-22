"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Copy } from "@/lib/copy";
import {
  decodeDigit,
  loadModel,
  predict,
  type Manifest,
  type Model,
  type Prediction,
} from "@/lib/model";
import { canvasToMnist, MNIST_SIZE } from "@/lib/preprocess";
import { drawDigit } from "@/lib/render";

const PAD = 280; // intern oppløsning på tegneflaten
const STROKE = 22; // ca. samme strekbredde/størrelsesforhold som MNIST har

type Props = {
  copy: Copy;
  manifest: Manifest;
  samples: string[];
  sampleLabels: number[];
};

export default function DrawDemo({ copy, manifest, samples, sampleLabels }: Props) {
  const padRef = useRef<HTMLCanvasElement>(null);
  const seenRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef(false);
  const frame = useRef(0);

  const [model, setModel] = useState<Model | null>(null);
  const [failed, setFailed] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [hasInk, setHasInk] = useState(false);

  // Vektene lastes én gang. AbortController rydder opp hvis noen navigerer
  // videre mens nedlastingen står på.
  useEffect(() => {
    const controller = new AbortController();
    loadModel(manifest, controller.signal)
      .then(setModel)
      .catch((err: unknown) => {
        if (!controller.signal.aborted) {
          console.error(err);
          setFailed(true);
        }
      });
    return () => controller.abort();
  }, [manifest]);

  const paintPad = useCallback(() => {
    const canvas = padRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }, []);

  useEffect(() => {
    const canvas = padRef.current;
    if (!canvas) return;
    canvas.width = PAD;
    canvas.height = PAD;
    paintPad();
  }, [paintPad]);

  /** Kjører forbehandling + nettverk på det som står på flaten nå. */
  const run = useCallback(() => {
    const canvas = padRef.current;
    if (!canvas || !model) return;

    const x = canvasToMnist(canvas);
    if (!x) {
      setResult(null);
      setHasInk(false);
      return;
    }
    setHasInk(true);
    setResult(predict(model, x));
    if (seenRef.current) drawDigit(seenRef.current, x);
  }, [model]);

  // Tegningen kan komme raskere enn vi vil regne, så vi samler opp til neste
  // bilde i stedet for å kjøre nettverket per musebevegelse. Bilderammen bes om
  // KUN når noe faktisk er endret — en løkke som ruller videre mens flaten står
  // stille koster batteri på mobil uten å gjøre noe.
  const schedule = useCallback(() => {
    if (frame.current !== 0) return;
    frame.current = requestAnimationFrame(() => {
      frame.current = 0;
      run();
    });
  }, [run]);

  useEffect(() => () => {
    if (frame.current !== 0) cancelAnimationFrame(frame.current);
  }, []);

  // Når vektene er ferdig lastet, regn ut det som eventuelt alt er tegnet.
  useEffect(() => {
    if (model) schedule();
  }, [model, schedule]);

  function positionOf(event: React.PointerEvent<HTMLCanvasElement>) {
    const canvas = padRef.current!;
    const rect = canvas.getBoundingClientRect();
    return {
      x: ((event.clientX - rect.left) / rect.width) * PAD,
      y: ((event.clientY - rect.top) / rect.height) * PAD,
    };
  }

  function start(event: React.PointerEvent<HTMLCanvasElement>) {
    const ctx = padRef.current?.getContext("2d");
    if (!ctx) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    drawing.current = true;

    const { x, y } = positionOf(event);
    ctx.strokeStyle = "#fff";
    ctx.fillStyle = "#fff";
    ctx.lineWidth = STROKE;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(x, y);
    // Et enkelt klikk skal også sette et merke, ikke bare et dra.
    ctx.arc(x, y, STROKE / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(x, y);
    schedule();
  }

  function move(event: React.PointerEvent<HTMLCanvasElement>) {
    if (!drawing.current) return;
    const ctx = padRef.current?.getContext("2d");
    if (!ctx) return;
    const { x, y } = positionOf(event);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
    schedule();
  }

  function end() {
    drawing.current = false;
    schedule();
  }

  function clear() {
    paintPad();
    setResult(null);
    setHasInk(false);
  }

  /** Maler et lagret MNIST-siffer inn på tegneflaten, så man kan prøve uten å tegne. */
  function useSample(b64: string) {
    const canvas = padRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const digit = decodeDigit(b64);
    const image = ctx.createImageData(MNIST_SIZE, MNIST_SIZE);
    for (let i = 0; i < digit.length; i++) {
      const v = Math.round(digit[i] * 255);
      image.data[i * 4] = v;
      image.data[i * 4 + 1] = v;
      image.data[i * 4 + 2] = v;
      image.data[i * 4 + 3] = 255;
    }

    // Vi må gjennom et mellomlerret for å skalere 28x28 opp til flatens
    // oppløsning; putImageData ignorerer transformasjoner.
    const scratch = document.createElement("canvas");
    scratch.width = MNIST_SIZE;
    scratch.height = MNIST_SIZE;
    scratch.getContext("2d")!.putImageData(image, 0, 0);

    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, PAD, PAD);
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(scratch, 0, 0, PAD, PAD);
    schedule();
  }

  const status = failed
    ? copy.demo.error
    : !model
      ? copy.demo.loading
      : !hasInk
        ? copy.demo.empty
        : null;

  return (
    <>
      <div className="demoGrid">
        <div>
          <div className="padWrap">
            <canvas
              ref={padRef}
              className="pad"
              onPointerDown={start}
              onPointerMove={move}
              onPointerUp={end}
              onPointerCancel={end}
              aria-label={copy.demo.drawHint}
            />
            <div className="padHint" style={{ opacity: hasInk ? 0 : 1 }}>
              {copy.demo.drawHint}
            </div>
          </div>

          <div className="padTools">
            <button type="button" className="btn" onClick={clear}>
              {copy.demo.clear}
            </button>
            <span className="badge">
              <span className="dot" />
              {copy.demo.offline}
            </span>
          </div>

          <p className="subhead">{copy.demo.examples}</p>
          <div className="samples">
            {samples.map((b64, i) => (
              <button
                key={i}
                type="button"
                className="sample"
                onClick={() => useSample(b64)}
                aria-label={`${copy.demo.examples} ${sampleLabels[i]}`}
              >
                <SampleThumb b64={b64} />
              </button>
            ))}
          </div>
          <p className="note">{copy.demo.examplesHint}</p>
        </div>

        <div>
          <div className="verdict">
            {status ? (
              <span className="verdictEmpty">{status}</span>
            ) : (
              <>
                <span className="verdictLabel">{copy.demo.verdict}</span>
                <span className="verdictDigit">{result?.digit}</span>
              </>
            )}
          </div>

          <p className="subhead">{copy.demo.activation}</p>
          <div className="bars">
            {Array.from({ length: 10 }, (_, d) => {
              const v = result ? result.out[d] : 0;
              return (
                <div className="bar" key={d} data-top={result?.digit === d}>
                  <span className="barDigit">{d}</span>
                  <span className="barTrack">
                    <span
                      className="barFill"
                      style={{ width: `${Math.max(v * 100, 0.6)}%` }}
                    />
                  </span>
                  <span className="barValue">{v.toFixed(3)}</span>
                </div>
              );
            })}
          </div>

          <p className="subhead">{copy.demo.preprocessed}</p>
          <div className="seenWrap">
            <canvas ref={seenRef} className="seen" width={MNIST_SIZE} height={MNIST_SIZE} />
            <p className="note" style={{ marginTop: 0 }}>
              {copy.demo.preprocessNote}
            </p>
          </div>

          <p className="subhead">{copy.demo.hidden}</p>
          <div className="hiddenGrid">
            {Array.from({ length: 128 }, (_, i) => {
              const a = result ? result.hidden[i] : 0;
              return (
                <span
                  key={i}
                  className="hiddenCell"
                  style={{
                    background: `rgba(217, 255, 99, ${(a * 0.95).toFixed(3)})`,
                  }}
                />
              );
            })}
          </div>
          <p className="note">{copy.demo.hiddenNote}</p>
        </div>
      </div>

      <p className="note">{copy.demo.notProbabilities}</p>
    </>
  );
}

/** Liten 28x28-forhåndsvisning i eksempelknappene. */
function SampleThumb({ b64 }: { b64: string }) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (ref.current) drawDigit(ref.current, decodeDigit(b64));
  }, [b64]);
  return <canvas ref={ref} width={MNIST_SIZE} height={MNIST_SIZE} />;
}
