# I built a neural network from scratch

**Target length:** ~7 minutes
**Voiceover:** English (ElevenLabs)
**On-screen text:** English
**Angle:** first person — this is what I built, what broke, and what it learned

Word count of VO below: ~1050, which lands around 7 min at normal narration pace with animation pauses.

---

## Scene 1 — The problem (0:00–0:45)

**Manim:** Black screen. A single MNIST digit fades in, large and centered. Then four more appear around it — messy ones, a 4 that looks like a 9, a 7 with a bar. Then all five shrink into a row.

**VO:**

> This is a five. You knew that instantly, and you have no idea how you knew it.
>
> There is no rule you could write down. No list of "if the top is flat and there's a loop at the bottom." People have tried, and it does not work, because every person writes a five slightly differently.
>
> So instead of writing the rules, I built something that finds the rules on its own. About four hundred lines of Python, no machine learning libraries, just NumPy for the matrix math. It gets ninety-seven and a half percent of handwritten digits right.
>
> Here's how it works.

**On-screen:**
- `no libraries. just NumPy.`
- `97.47% accuracy`

---

## Scene 2 — From image to numbers (0:45–1:25)

**Manim:** Zoom into the five until the pixel grid is visible. Overlay the grid lines. Numbers appear in each cell — 0 in the dark ones, values up to 255 in the bright ones. Then the 28 rows unfold and stack into one tall column. Label it 784.

**VO:**

> A computer doesn't see a five. It sees a grid — twenty-eight by twenty-eight, seven hundred and eighty-four little squares, each holding a brightness value from zero to two fifty-five.
>
> First thing I do is divide everything by two fifty-five, so every pixel sits between zero and one. That matters more than it sounds like, and I'll come back to why.
>
> Then I unroll the grid. Row by row, into one long column of seven hundred and eighty-four numbers. The image is now just a list. That's the input.

**On-screen:**
- `28 × 28 = 784`
- `pixel ÷ 255 → [0, 1]`

**Note:** the unroll animation is the visual hook of the whole video. Worth spending time on.

---

## Scene 3 — One neuron (1:25–2:35)

**Manim:** Clear to a single circle on the right. Four input circles on the left with values in them (simplify to 4 inputs, note on screen that the real one has 784). Weight numbers appear on each arrow. Products pop up, then slide together into a sum. Bias slides in and adds. The result — a single number, maybe 3.7 — sits above the neuron.

Then the sigmoid curve from Scene 4 slides in from the side, the number travels along the x-axis, hits the curve, and comes out as a fill color in the neuron.

**VO:**

> Here's the piece everything is built from. One neuron.
>
> A neuron looks at its inputs and asks one question. Something like: is there a horizontal stroke near the top of this image?
>
> It answers by voting. Every input gets a weight. Positive weight means "I want brightness here." Negative means "I want darkness here." Zero means "I don't care." Multiply each input by its weight, add them all up, and add one more number called the bias — that's the threshold, how much evidence this neuron needs before it speaks up.
>
> What comes out is one number. I call it z. It can be anything — minus twelve, zero point three, forty-seven.
>
> And then I squash it.

**On-screen:**
- `z = w₁x₁ + w₂x₂ + ... + b`
- `(showing 4 inputs — the real thing has 784)`

---

## Scene 4 — Sigmoid, and why (2:35–3:15)

**Manim:** The sigmoid curve on axes. A dot moves along it, driven by a ValueTracker, with a tangent line attached. Drag the dot out to z = 8 — the tangent goes flat. Flash that region red briefly.

**VO:**

> This is the sigmoid function. Feed it any number, it gives you back something between zero and one. Big negative goes to zero, big positive goes to one, and zero goes to exactly a half.
>
> So z is "how much evidence did I gather," and the output is "how confident am I, from zero to one."
>
> But here's the real reason it's there. Without it, every layer would just be multiplication and addition — and stacking two of those gives you something you could have done in one. A hundred layers would be no more powerful than one. The sigmoid is what makes depth mean anything.
>
> Watch what happens out here, though. When z gets large, the curve goes flat. Nudging z does nothing. The neuron is saturated, and saturated neurons stop learning. That's why the pixels get divided by 255, and why the starting weights get scaled down — to keep z in the part of the curve that still has a slope.

**On-screen:**
- `σ(z) = 1 / (1 + e⁻ᶻ)`
- `flat curve → no learning`

---

## Scene 5 — Layers and matrices (3:15–3:55)

**Manim:** Zoom out to show 784 inputs feeding one neuron, then duplicate to 128 neurons. The tangle of lines collapses into a clean rectangle labeled W, shape (784, 128). Show `X @ W + b` as three blocks combining.

**VO:**

> One neuron asks one question. A layer is a hundred and twenty-eight neurons asking a hundred and twenty-eight different questions at the same time.
>
> Each one has its own seven hundred and eighty-four weights, so I stack them into a grid — a matrix. Seven eighty-four by one twenty-eight.
>
> And now the whole layer is one line of code. Inputs times weights, plus bias. That's not new math, it's just bookkeeping. The matrix multiply does a hundred thousand multiply-and-adds in a single operation, and it does it for thirty-two images at once.
>
> Then a second layer takes those hundred and twenty-eight answers down to ten. One output per digit.

**On-screen:**
- `Z = X @ W + b`
- `784 → 128 → 10`

---

## Scene 6 — Forward pass and loss (3:55–4:35)

**Manim:** Reuse your existing architecture scene. Wave of activation propagating left to right, neurons lighting up by value. Output column of 10 appears. Beside it, the one-hot target. Subtract elementwise, square, sum to one number.

**VO:**

> Push an image through both layers and you get ten numbers out. How strongly the network believes in each digit.
>
> Untrained, they're all about a half. It has no idea.
>
> To fix that I need to measure how wrong it is. The correct answer for a five is this — a one in slot five, zeros everywhere else. Subtract, square each difference so the negatives don't cancel, add them up. One number. The loss.
>
> Untrained, mine started at two point seven. The whole job now is making that number smaller.

**On-screen:**
- `target: [0,0,0,0,0,1,0,0,0,0]`
- `loss = 2.72`

---

## Scene 7 — Gradient descent (4:35–5:15)

**Manim:** A ball on a 1D curve, rolling downhill in steps. Then show a too-large learning rate — ball overshoots and bounces out. Then switch to a 3D surface with ThreeDScene and roll down that. Caption: "now imagine 101,770 dimensions."

**VO:**

> There are a hundred thousand weights in this network, and the loss depends on every single one of them.
>
> Picture it as a landscape. Every position is one setting of all the weights, and the height is the loss. I want the bottom of the valley.
>
> I can't see the landscape — it has a hundred thousand dimensions. But I can feel the slope under my feet. So I take a small step downhill, and repeat.
>
> Step too big and you fly straight over the valley and end up worse than you started. Step too small and you're there all week. That's the learning rate, and mostly you find it by trying.

**On-screen:**
- `101,770 parameters`
- `learning rate = 1.0`

---

## Scene 8 — Backpropagation (5:15–5:55)

**Manim:** The network again. Red error arrows at the output, flowing backwards layer by layer. Each weight flashes with intensity proportional to `abs(dW)` — use real gradients from your `backward`.

**VO:**

> So I need the slope. For every weight, how much would the loss change if I nudged this one thing?
>
> A hundred thousand weights, and I need all of them, for every image. That sounds impossible, and for a long time it basically was.
>
> The trick is called backpropagation. Start at the output, where the error is obvious — you can see exactly what it got wrong. Then push that error backwards. Each layer hands blame to the layer before it, weighted by how much each connection contributed. Four equations, one pass backwards, and you get every gradient at once.
>
> That's the whole idea. Blame flows backwards.

**On-screen:**
- `error flows backwards`

---

## Scene 9 — Was it right? (5:55–6:20)

**Manim:** Split screen. Left: the four backprop equations. Right: a terminal-style block showing the actual gradient check output — numerical vs analytical vs relative error. Highlight the `1e-10` column.

**VO:**

> Now, I wrote those four equations myself, and there was no way to know if I'd got them right. Gradients with a bug in them still have the correct shape. They just quietly point the wrong way.
>
> So I checked them the slow way. Take one weight, nudge it up a hair, measure the loss. Nudge it down, measure again. Divide by how far I moved it — that's the slope, straight from the definition. Painfully slow, but I only needed a handful.
>
> The two methods agreed to ten decimal places. That's the moment I knew the math was right.

**On-screen:**
- `numerical:   0.10971767`
- `analytical:  0.10971767`
- `rel. error: 1.0e-11 ✓`

---

## Scene 10 — Training (6:20–6:50)

**Manim:** Loss curve drawing itself from real data in your `.npz`. Accuracy climbing beside it. Epoch counter ticking.

**VO:**

> Then it's just: show it thirty-two images, measure the error, nudge every weight downhill, repeat. Eighteen hundred and seventy-five times per pass through the data. Ten passes.
>
> After one pass it was already at ninety-three percent. After ten, ninety-seven point five.
>
> Loss went down every single epoch, and accuracy climbed almost all the way — one small wobble near the end. No blow-ups, no plateau. That smoothness is what correct backprop looks like.

**On-screen:**
- `epoch 1  — 93.02%`
- `epoch 10 — 97.47%`

---

## Scene 11 — What it learned, and what it missed (6:50–7:30)

**Manim:** Grid of the 128 first-layer weight vectors reshaped to 28×28. Show epoch 0 (noise) then epoch 10 (structured noise). Then cut to the 20 most confident misclassifications with `true → predicted` labels.

**VO:**

> Here's what the hidden layer actually learned — each square is one neuron's weights, drawn back out as an image.
>
> I was expecting stroke detectors. Clean little edges and curves. That's not what I got. It's structured noise. The network found something that works, not something that explains itself. That's worth sitting with.
>
> And these are the ones it got wrong, ranked by how confident it was while being wrong. Some of them are genuinely ambiguous. A few are mislabeled in the dataset itself. The last two and a half percent isn't only a model problem.
>
> Ninety-seven point five percent. About four hundred lines. No libraries.
>
> Every equation in this video is one I typed out and got wrong at least once first.

**On-screen:**
- `true → predicted`
- `97.47%`

---

## Production notes

**Scene build order** (easiest first, not narrative order): 4 → 2 → 6 → 10 → 11 → 3 → 5 → 8 → 7 → 9 → 1.

**Voice pick:** for this kind of explainer, try Adam or Josh from the default ElevenLabs library — calm, mid-pace, not over-performed. Generate Scene 1 with two or three voices before committing; you'll be listening to it a lot.

**Prompting the VO:** ElevenLabs respects punctuation for pacing. Em-dashes and short sentences give you natural breathing room. Where a line needs to sit still while an animation runs, add a trailing period or split into two `voiceover` blocks rather than stretching the animation over silence.

**Cutting to length:** if this runs long, Scene 9 (gradient check) is the first to shorten and Scene 7 (gradient descent) the second. Keep Scene 11 whole — the "it's structured noise" beat is the most honest thing in the script and the reason to watch to the end.

**Numbers to double check before recording:** all figures above are from your actual run. If you retrain after moving the shuffle inside the epoch loop, the accuracy will likely change — update Scenes 1, 10, and 11.

---

## Hvordan filmen bygges

Alle tall som vises på skjermen kommer fra én ekte treningskjøring, lagret i `artifacts/run.npz`:

```
make artifacts     # trener 10 epoker og lagrer vekter, loss, treff og bom
make video         # rendrer alle 11 scenene i 720p30 og skjøter dem sammen
make video-hq      # samme i 1080p60
make video-vo      # samme, men med ElevenLabs-voiceover (bruker API-kreditter)
```

Hver scene ligger i `scenes/sNN_*.py` og arver `NarratedScene` fra `scenes/common.py`.
Replikkene ligger i `self.narrate(...)`-blokker: uten `VOICEOVER=1` beregnes lengden
ut fra teksten, med `VOICEOVER=1` byttes de mot ekte `manim-voiceover`-blokker uten at
scenekoden endres.

### Voiceover

`make video-vo` kjører `prepare_vo.py` først, som genererer alle 48 replikkene (~6 800
tegn = ~6 800 ElevenLabs-credits) med retry og backoff, og legger dem i
`media/voiceovers/`. Først når hele cachen er på plass starter rendringen — ellers
ryker hele bygget hvis ett API-kall møter «heavy traffic». Cachen er nøklet på teksten,
så rerender koster ingenting; bare replikker du endrer ordlyden på genereres på nytt.

Stemme og modell styres med miljøvariabler: `VOICE_NAME` (standard Adam), `VOICE_ID`,
`VOICE_MODEL` (standard `eleven_multilingual_v2` — kvalitetsmodellen, også for engelsk;
`eleven_flash_v2_5` er halv pris og lavere kvalitet).

API-nøkkelen her mangler `voices_read`, og `manim-voiceover` slår alltid opp stemmelista
selv når du gir den en id. `DirectVoiceService` i `scenes/common.py` går derfor rett på
voice_id. Gir du nøkkelen `voices_read` senere, kan den klassen erstattes med
`ElevenLabsService`.

Denne maskinen har ingen LaTeX-installasjon, så alle formler er satt i monospace `Text`
i stedet for `MathTex`. Legger du inn LaTeX senere kan de byttes ut scene for scene.

**Tall fra kjøringen filmen er bygget på:** første loss 2.71, epoke 1 = 93.02 %,
epoke 10 = 97.47 %, 101 770 parametre, gradientsjekk ned til 1.0e-11.