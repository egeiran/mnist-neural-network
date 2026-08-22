# web/

The site behind [mnist.eivindgeiran.no](https://mnist.eivindgeiran.no). Next.js
15, TypeScript, no CSS framework, deployed on Vercel with `web/` as the project
root.

The interesting part is that the trained network runs client-side. There is no
inference API: the 101,770 parameters download once as a 199 KB float16 file and
the forward pass — two matrix multiplications and a sigmoid — happens in the
visitor's browser.

## Running it

The site reads generated data, so export that first:

```bash
python tools/export_web.py     # from the repo root: run.npz → weights + figures
cd web && npm install && npm run dev
```

`tools/export_web.py` writes two things, both committed:

- `public/model/mnist-784-128-10.f16` — W1, b1, W2, b2 back to back as
  little-endian float16
- `src/data/run.json` — every figure the page displays

Nothing on the page is a hard-coded number. Retrain, re-run the export, and the
site describes the new run.

## Layout

```
src/app/         layout, global stylesheet, the single page
src/components/  Site (composition), DrawDemo, Film, Charts, Misses
src/lib/         model (inference), preprocess (canvas → MNIST), copy (NO/EN), site (links)
src/data/        run.json, generated
public/model/    the weights, generated
```

`src/lib/copy.ts` holds all text in both Norwegian and English; no copy lives
inside a component. `src/lib/site.ts` holds outbound links and the video ID.

## Two things that are easy to get wrong

**Preprocessing decides whether the demo works.** MNIST digits are not raw
images — each is cropped to its bounding box, scaled so the longer side is 20
pixels, and placed in a 28×28 field so its *centre of mass* lands in the middle.
A network trained on them has never seen anything else. Scaling a drawing
straight down to 28×28 produces systematic misses that look like a bad model but
are really bad input. `src/lib/preprocess.ts` reproduces the original
normalisation.

**float16 has to be shown to be free.** Halving the download is only worth it if
it changes no predictions. Two checks cover this: `tools/export_web.py` refuses
to write the file if float16 flips a single prediction, and
`tools/check_web_model.{py,ts}` runs 57 real MNIST images through both NumPy and
the browser implementation and compares them. Largest deviation in output
activation: `6.7e-4`, with zero changed predictions.

## Chapter marks

`SITE.chapters` lists the film's scenes with a start time each. They are shown
on the page only when `SITE.chaptersVerified` is true, because the times
currently stored are the scene boundaries from `manus.md` — estimates written
before the film was rendered, not measurements taken from it. With real
narration each scene runs as long as its audio does, so the later marks drift. A
chapter that jumps to the wrong moment is worse than no chapters, so they stay
hidden until the times are measured.

## Deployment

Vercel, with **Root Directory** set to `web`. There are no environment
variables — the page is fully static and holds no secrets. The one non-default
piece of configuration is in `vercel.json`: the weights file is immutable and
content-addressed by name, so it is served with a one-year cache.
