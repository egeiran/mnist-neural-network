"use client";

import { useEffect, useState } from "react";
import { COPY, type Lang } from "@/lib/copy";
import { SITE } from "@/lib/site";
import run from "@/data/run.json";
import DrawDemo from "./DrawDemo";
import Film from "./Film";
import Charts from "./Charts";
import { Confusion, Filters, Misses } from "./Misses";
import type { Manifest } from "@/lib/model";

const manifest = run.model as Manifest;

export default function Site() {
  const [lang, setLang] = useState<Lang>("no");
  const copy = COPY[lang];

  // <html lang> må følge språkvalget for skjermlesere og for at nettleseren
  // skal orddele riktig. Siden bytter uten omlasting, så vi setter den her.
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  return (
    <>
      <header className="top">
        <div className="shell topInner">
          <span className="mark">
            784 <span>→</span> 128 <span>→</span> 10
          </span>
          <nav className="topLinks">
            <a href="#demo">{copy.nav.demo}</a>
            <a href="#film">{copy.nav.video}</a>
            <a href={SITE.repo} target="_blank" rel="noopener noreferrer">
              {copy.nav.repo}
            </a>
            <span className="langToggle">
              {(["no", "en"] as Lang[]).map((code) => (
                <button
                  key={code}
                  type="button"
                  data-active={lang === code}
                  onClick={() => setLang(code)}
                  aria-pressed={lang === code}
                >
                  {code.toUpperCase()}
                </button>
              ))}
            </span>
          </nav>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="shell">
            <p className="eyebrow">{copy.hero.eyebrow}</p>
            <h1>{copy.hero.title}</h1>
            <p className="lede">{copy.hero.lede}</p>
            <div className="stats">
              {copy.hero.stats.map((stat) => (
                <div className="stat" key={stat.label}>
                  <div className="statValue">{stat.value}</div>
                  <div className="statLabel">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="demo">
          <div className="shell">
            <h2>{copy.demo.title}</h2>
            <p className="lede">{copy.demo.lede}</p>
            <DrawDemo
              copy={copy}
              manifest={manifest}
              samples={run.sampleImages}
              sampleLabels={run.sampleLabels}
            />
          </div>
        </section>

        <section id="film">
          <div className="shell">
            <h2>{copy.video.title}</h2>
            <p className="lede">{copy.video.lede}</p>
            <Film copy={copy} lang={lang} />
          </div>
        </section>

        <section id="how">
          <div className="shell">
            <h2>{copy.how.title}</h2>
            <p className="lede">{copy.how.lede}</p>

            <div className="arch">
              <div className="layer">
                <div className="layerN">784</div>
                <div className="layerLabel">{copy.how.arch.pixels}</div>
              </div>
              <div className="arrow">
                →<small>100 352 {copy.how.arch.weights}</small>
              </div>
              <div className="layer">
                <div className="layerN">128</div>
                <div className="layerLabel">{copy.how.arch.hidden}</div>
              </div>
              <div className="arrow">
                →<small>1 280 {copy.how.arch.weights}</small>
              </div>
              <div className="layer">
                <div className="layerN">10</div>
                <div className="layerLabel">{copy.how.arch.digits}</div>
              </div>
            </div>

            <div className="steps">
              {copy.how.steps.map((step, i) => (
                <article className="step" key={step.title}>
                  <div className="stepNum">0{i + 1}</div>
                  <h3>{step.title}</h3>
                  <p>{step.body}</p>
                </article>
              ))}
            </div>

            <p className="subhead">{copy.how.codeCaption}</p>
            <pre>
              <code>
                <span className="cm">{"# nn/network.py\n\n"}</span>
                <span className="kw">def</span> <span className="fn">forward</span>
                {"(X, Ws, bs):\n"}
                {"    As = [X]\n"}
                {"    Zs = []\n"}
                {"    "}
                <span className="kw">for</span> {"W, b "}
                <span className="kw">in</span> {"zip(Ws, bs):\n"}
                {"        Z = As[-1] @ W + b\n"}
                {"        Zs.append(Z)\n"}
                {"        As.append(sigmoid(Z))\n"}
                {"    "}
                <span className="kw">return</span> {"As[-1], Zs, As"}
              </code>
            </pre>
          </div>
        </section>

        <section id="gradcheck">
          <div className="shell">
            <h2>{copy.gradcheck.title}</h2>
            <p className="lede">{copy.gradcheck.lede}</p>
            <pre>
              <code>{run.gradcheck}</code>
            </pre>
            <p className="caption">{copy.gradcheck.caption}</p>
            <p className="takeaway">{copy.gradcheck.takeaway}</p>
          </div>
        </section>

        <section id="training">
          <div className="shell">
            <h2>{copy.training.title}</h2>
            <p className="lede">{copy.training.lede}</p>
            <Charts
              copy={copy}
              lossCurve={run.lossCurve}
              epochAccuracy={run.epochAccuracy}
            />
          </div>
        </section>

        <section id="learned">
          <div className="shell">
            <h2>{copy.learned.title}</h2>
            <p className="lede">{copy.learned.lede}</p>
            <Filters copy={copy} filters={run.filters} />
          </div>
        </section>

        <section id="misses">
          <div className="shell">
            <h2>{copy.misses.title}</h2>
            <p className="lede">{copy.misses.lede}</p>
            <Misses copy={copy} worst={run.worst} images={run.worstImages} />

            <h3 style={{ marginTop: 56, fontSize: 22 }}>{copy.misses.confusionTitle}</h3>
            <p className="lede" style={{ marginTop: 12 }}>
              {copy.misses.confusionLede}
            </p>
            <Confusion copy={copy} matrix={run.confusion} top={run.topConfusions} />
          </div>
        </section>

        <section id="honest" className="honest">
          <div className="shell">
            <h2>{copy.honest.title}</h2>
            {copy.honest.body.map((paragraph) => (
              <p key={paragraph.slice(0, 40)}>{paragraph}</p>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <div className="shell">
          <div className="footRow">
            <a href={SITE.repo} target="_blank" rel="noopener noreferrer">
              {copy.footer.source}
            </a>
            <a href={SITE.home}>{copy.footer.back}</a>
          </div>
          <p style={{ margin: 0, maxWidth: "70ch" }}>{copy.footer.colophon}</p>
        </div>
      </footer>
    </>
  );
}
