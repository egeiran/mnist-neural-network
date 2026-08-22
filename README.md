# A neural network from scratch

A 784 → 128 → 10 neural network that recognises handwritten digits, written in
plain NumPy with no machine learning library. Backpropagation is derived by hand
and verified against numerical gradients. It gets **97.47 %** of the MNIST test
set right.

Then I made a film explaining how it works, animated in
[Manim](https://www.manim.community/), where every number on screen comes from
the same training run that produced the weights.

**[Watch the film](https://youtu.be/3KQHb3Rx8PM)** · **[mnist.eivindgeiran.no](https://mnist.eivindgeiran.no)** — draw a digit and
run the real trained weights in your browser.

---

## The numbers

| | |
|---|---|
| Architecture | 784 → 128 → 10, sigmoid in both layers |
| Parameters | 101,770 |
| Loss | mean squared error |
| Training | 10 epochs, batch size 32, learning rate 1.0, 18,750 steps |
| First loss | 2.708 |
| Accuracy after epoch 1 | 93.02 % |
| Accuracy after epoch 10 | **97.47 %** |
| Gradient check | agrees to `1.0e-11` |
| Test errors | 253 of 10,000 |

Every figure above comes from a single training run stored in
`artifacts/run.npz`. This table is transcribed from it by hand; the website
generates its numbers from the same file at build time, so if the two ever
disagree, the website is right.

## Why no library

Calling `model.fit()` teaches you the API. Deriving the chain rule through two
layers, getting a sign wrong, and watching the network still train — just
slightly worse — teaches you what the library is doing.

That last part is the reason `nn/network.py` has a `grad_check()` function. A
backprop implementation with a subtle error does not crash; it converges to
something a bit worse and hides. The only way to know the derivation is right is
to nudge a single weight by ±1e-5, measure how the loss actually moves, and
compare it to what backprop claimed:

```
W[1][2,1]  num=0.10971767  ana=0.10971767  rel=1.01e-11
```

Eleven digits of agreement. That is as close as floating point gets.

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

make train        # train and print accuracy per epoch
make train-live   # same, with a live view of the weights forming
make test         # run the gradient check
make artifacts    # train and save everything the film and site need to run.npz
```

`nn/data.py` pulls MNIST from OpenML through scikit-learn the first time; after
that it is cached locally. scikit-learn is used **only** to fetch the dataset —
never for the network itself.

Training and the gradient check need nothing but `numpy`, `scikit-learn` and
`matplotlib`. Manim additionally builds against system Cairo and Pango, so
rendering the film needs those present first — on Debian/Ubuntu
`libcairo2-dev libpango1.0-dev pkg-config`, on macOS `brew install cairo pango
pkg-config`. Without them `pip install manimpango` fails at the wheel build with
a `pkg-config … pangocairo` error.

## The film

```bash
make video        # all 11 scenes at 720p30, stitched into one file
make video-hq     # 1080p60
make video-vo     # with ElevenLabs narration (uses API credits)
```

Each scene lives in `scenes/sNN_*.py` and inherits `NarratedScene` from
`scenes/common.py`. Narration sits in `self.narrate(...)` blocks: without
`VOICEOVER=1` the timing is estimated from the text, with it the blocks become
real `manim-voiceover` blocks without the scene code changing.

`manus.md` holds the full script and the production notes. `PREVIEW.md` covers
the fast iteration loop — `make preview` for a live OpenGL window, `make still`
for a single frame in ~4 seconds instead of a 15 second render, and why
`--disable_caching` is the default here (with 784 squares in a grid, hashing the
mobject tree costs more than the cache saves — a fully warm cache measured
*slower* than rendering everything fresh).

## The website

`web/` is a Next.js app deployed at
[mnist.eivindgeiran.no](https://mnist.eivindgeiran.no). The interesting part is
that the trained network runs client-side: the 101,770 parameters ship as a
199 KB float16 file, and the forward pass is two matrix multiplications in
JavaScript. No inference server, nothing leaves the browser.

```bash
make web          # run.npz → weights + figures for the site
make check-web    # verify the browser computes what NumPy does
cd web && npm install && npm run dev
```

Two things that are easy to get wrong there, and are handled:

**Preprocessing.** MNIST digits are size-normalised into a 20×20 box and centred
by *centre of mass* in a 28×28 field. Scale a canvas drawing straight down to
28×28 and the network misses constantly — it has never seen anything shaped like
that. `web/src/lib/preprocess.ts` reproduces the original normalisation.

**Precision.** Shipping float16 weights halves the download, so it has to be
shown to cost nothing. `make check-web` runs the same 57 real MNIST images
through NumPy and through the browser implementation and compares them. Largest
deviation in output activation: `6.7e-4`, with zero changed predictions. The
export refuses to write the weights at all if float16 flips a single
prediction.

## Layout

```
nn/            the network — data loading, forward, backward, training
scenes/        one Manim scene per section of the film
tools/         weight export for the web demo, plus its verification
web/           the Next.js site behind mnist.eivindgeiran.no
artifacts/     run.npz — one real training run, the source of every number
manus.md       the film script and production notes
PREVIEW.md     how to iterate on scenes without waiting for renders
```

## What I would do differently

A sigmoid output layer with squared error is not what you would choose today.
Softmax with cross-entropy gives gradients that do not vanish when the network is
confidently wrong, and would likely train faster to a better result. ReLU in the
hidden layer would fix the same problem there — with sigmoid in both layers the
gradient shrinks on the way back, which is much of why the learning rate had to
be 1.0 to get anywhere.

And 97.47 % is roughly the ceiling for a fully connected network on MNIST. A
convolutional network passes 99 % because it knows neighbouring pixels belong
together — information thrown away the moment the image is unrolled into a list
of 784 numbers.

Those are the next things to build, not regrets. The point of this one was to
understand every line of it.

---

Eivind Geiran · [eivindgeiran.no](https://eivindgeiran.no)
