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
make web          # from the repo root: run.npz → weights + figures
make check-web    # verify the browser computes what NumPy does
cd web && npm install && npm run dev
```

`tools/export_web.py` writes two things, both committed:

- `public/model/mnist-<sizes>-<hash>.f16` — W1, b1, W2, b2 back to back as
  little-endian float16, named by a hash of its own contents
- `src/data/run.json` — every figure the page displays

No figure on the page is hard-coded. `src/lib/copy.ts` is a function of the run
data rather than a constant, so the sentences, the hero stats, the chart axes
and the architecture diagram all read from `run.json`. Retrain, re-run the
export, and the page describes the new run — including the prose.

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
it changes no predictions. `make check-web` covers this: `tools/export_web.py`
refuses to write the file if float16 flips a single prediction, and
`tools/check_web_model.{py,ts}` runs 57 real MNIST images through both NumPy and
the browser implementation and compares them. Largest deviation in output
activation: `6.7e-4`, with zero changed predictions.

The same check verifies that each image in the "what it gets wrong" section
still belongs to its caption. The page pairs `worst[i]` with `worstImages[i]`,
and if the two lists ever fall out of order nothing throws — the picture just
stops matching the words underneath it.

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
piece of configuration is in `vercel.json`: `/model/*` is served with a one-year
`immutable` cache. That is only safe because the export puts a hash of the
weights in the filename — `mnist-784-128-10-<sha8>.f16` — so retraining
produces a new name and no returning visitor can be served last year's weights
against this year's figures.
