import { ImageResponse } from "next/og";
import run from "@/data/run.json";

// Genereres ved bygging, så tallene følger treningskjøringen som resten av
// siden. Uten dette blir delinger på LinkedIn og Slack rene tekstlenker.
export const alt = "A neural network from scratch — 784 → 128 → 10 in plain NumPy";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  const accuracy = (run.finalAccuracy * 100).toFixed(2);
  const params = new Intl.NumberFormat("en-US").format(run.parameters);
  const [inputs, hidden, outputs] = run.architecture;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#0c0e11",
          padding: 72,
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", color: "#d9ff63", fontSize: 30, letterSpacing: 4 }}>
          MNIST · NUMPY · MANIM
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <div style={{ display: "flex", color: "#f4f1e8", fontSize: 76, lineHeight: 1.1 }}>
            A neural network
          </div>
          <div style={{ display: "flex", color: "#f4f1e8", fontSize: 76, lineHeight: 1.1 }}>
            from scratch.
          </div>
          <div style={{ display: "flex", color: "#8b93a0", fontSize: 32, marginTop: 12 }}>
            {inputs} → {hidden} → {outputs} · no ML library · draw a digit and run it
          </div>
        </div>

        <div style={{ display: "flex", gap: 56, alignItems: "flex-end" }}>
          {[
            [`${accuracy}%`, "accuracy"],
            [params, "parameters"],
            ["0", "ML libraries"],
          ].map(([value, label]) => (
            <div key={label} style={{ display: "flex", flexDirection: "column" }}>
              <div style={{ display: "flex", color: "#d9ff63", fontSize: 48 }}>{value}</div>
              <div style={{ display: "flex", color: "#8b93a0", fontSize: 24 }}>{label}</div>
            </div>
          ))}
          <div
            style={{
              display: "flex",
              marginLeft: "auto",
              color: "#8b93a0",
              fontSize: 26,
            }}
          >
            mnist.eivindgeiran.no
          </div>
        </div>
      </div>
    ),
    size,
  );
}
