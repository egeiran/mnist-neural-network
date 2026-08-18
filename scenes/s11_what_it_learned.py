"""Scene 11 — What it learned, and what it missed (6:50–7:30)."""

import numpy as np
from manim import *

from scenes.common import (
    ACCENT,
    BG,
    DIM,
    FG,
    GOLD,
    GREEN,
    MUTED,
    NarratedScene,
    WARM,
    body,
    chips,
    digit_image,
    image_from_array,
    mono,
    place_chips,
    run,
    weight_scale,
    weight_sheet,
)

ROWS, COLS, GAP = 8, 16, 2
SHEET_H = 5.0


def sheet_frames(snaps: np.ndarray) -> np.ndarray:
    """Alle vekt-øyeblikksbildene → én stabel ferdige ark, (n, h, w, 3) uint8.

    Én felles fargeskala for hele stabelen, hentet fra sluttvektene: da er det
    veksten i vektene man ser, ikke at normaliseringen flytter på seg.
    """
    scale = weight_scale(snaps[-1])
    return np.stack(
        [weight_sheet(np.asarray(W, dtype=np.float32), ROWS, COLS, GAP, scale) for W in snaps]
    )


def morph_updater(frames: np.ndarray, idx: ValueTracker):
    """Skriver rett i ImageMobject-ets pikselbuffer hver frame, og interpolerer
    mellom nabo-snapshots — ellers blir tidsforløpet hakkete lysbilder."""

    def update(mob):
        f = float(np.clip(idx.get_value(), 0, len(frames) - 1))
        i = int(f)
        j = min(i + 1, len(frames) - 1)
        a = f - i
        blend = (1 - a) * frames[i].astype(np.float32) + a * frames[j].astype(np.float32)
        mob.pixel_array[..., :3] = blend.astype(np.uint8)

    return update


class S11WhatItLearned(NarratedScene):
    def construct(self):
        data = run()
        W1_init = data["W1_init"]
        W1_final = data["W1_final"]
        acc = float(data["epoch_acc"][-1]) * 100
        worst_imgs = data["worst_images"]
        worst_true = data["worst_true"]
        worst_pred = data["worst_pred"]

        # Vektene slik de så ut gjennom hele treningen. Eldre run.npz har bare
        # start og slutt — da blir «tidsforløpet» en enkel overtoning.
        if "W1_snaps" in data.files:
            snaps = np.asarray(data["W1_snaps"])
            steps = np.asarray(data["snap_steps"])
        else:
            snaps = np.stack([W1_init, W1_final])
            steps = np.array([0, 18750])

        frames = sheet_frames(snaps)
        total_steps = int(steps[-1])

        sheet = image_from_array(frames[0].copy(), height=SHEET_H).move_to(DOWN * 0.25)
        idx = ValueTracker(0.0)
        morph = morph_updater(frames, idx)

        with self.narrate(
            "Here's what the hidden layer actually learned — each square is one neuron's "
            "weights, drawn back out as an image. Watch them form."
        ) as t:
            caption = mono("128 hidden neurons  ·  784 weights each, folded back to 28 × 28",
                           size=20, color=MUTED)
            caption.next_to(sheet, DOWN, buff=0.45)
            stamp = mono("before training", size=24, color=MUTED)
            stamp.next_to(sheet, UP, buff=0.4)
            anchor = stamp.get_center()

            self.play(FadeIn(sheet), FadeIn(stamp), run_time=1.0)
            self.play(FadeIn(caption), run_time=0.6)
            sheet.add_updater(morph)

            # Snapshotene er log-spredte, så jevn spilletid per segment gir
            # sakte film der det skjer mest — de første hundre batchene.
            segments = 8
            budget = max(t.get_remaining_duration() - 0.8, 4.0)
            edges = np.linspace(0, len(frames) - 1, segments + 1)
            for k in range(segments):
                if k > 0:
                    self.remove(stamp)
                    stamp = mono(
                        f"batch {int(steps[int(round(edges[k]))]):,} / {total_steps:,}",
                        size=24, color=GOLD,
                    ).move_to(anchor)
                    self.add(stamp)
                self.play(
                    idx.animate.set_value(float(edges[k + 1])),
                    run_time=budget / segments,
                    rate_func=linear,
                )

            sheet.remove_updater(morph)
            self.remove(stamp)
            stamp = mono("after 10 epochs", size=24, color=ACCENT).move_to(anchor)
            self.play(FadeIn(stamp), run_time=0.5)

        with self.narrate(
            "I was expecting stroke detectors. Clean little edges and curves. That's not what "
            "I got. It's structured noise. The network found something that works, not "
            "something that explains itself. That's worth sitting with."
        ) as t:
            picks = [18, 53, 97]
            tile_w = sheet.width / COLS
            tile_h = sheet.height / ROWS
            boxes = VGroup()
            for k in picks:
                r, c = divmod(k, COLS)
                center = sheet.get_corner(UL) + np.array(
                    [(c + 0.5) * tile_w, -(r + 0.5) * tile_h, 0]
                )
                boxes.add(Rectangle(width=tile_w * 0.94, height=tile_h * 0.94,
                                    color=GOLD, stroke_width=2).move_to(center))
            self.play(LaggedStart(*[Create(b) for b in boxes], lag_ratio=0.3), run_time=1.2)

            expected = body("expected: edges and strokes", 24, MUTED).to_edge(UP, buff=0.5)
            self.play(FadeIn(expected), run_time=0.7)
            self.wait(min(1.6, max(t.get_remaining_duration() - 2.4, 0.2)))
            got = body("got: structured noise", 24, GOLD).move_to(expected)
            self.play(Transform(expected, got), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.6, 0.2))
            self.play(
                FadeOut(sheet), FadeOut(boxes), FadeOut(caption),
                FadeOut(stamp), FadeOut(expected),
                run_time=0.7,
            )

        # --- De den bommet på ------------------------------------------------
        with self.narrate(
            "And these are the ones it got wrong, ranked by how confident it was while being "
            "wrong. Some of them are genuinely ambiguous. A few are mislabeled in the dataset "
            "itself. The last two and a half percent isn't only a model problem."
        ) as t:
            cells = Group()
            for img, tr, pr in zip(worst_imgs, worst_true, worst_pred):
                pic = digit_image(img, height=0.95)
                lab = mono(f"{int(tr)} → {int(pr)}", size=17, color=WARM)
                lab.next_to(pic, DOWN, buff=0.1)
                cells.add(Group(pic, lab))

            for i, cell in enumerate(cells):
                r, c = divmod(i, 5)
                cell.move_to(np.array([(c - 2) * 2.15, 1.75 - r * 1.55, 0]))

            title = body("wrong, and confident about it", 26, FG).to_edge(UP, buff=0.4)
            self.play(FadeIn(title), run_time=0.5)
            self.play(
                LaggedStart(*[FadeIn(c, scale=0.9) for c in cells], lag_ratio=0.06),
                run_time=2.4,
            )
            legend = chips("true → predicted", color=WARM).to_corner(UR, buff=0.5)
            self.play(FadeIn(legend), run_time=0.5)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.2))
            self.play(FadeOut(cells), FadeOut(title), FadeOut(legend), run_time=0.8)

        # --- Sluttkort --------------------------------------------------------
        with self.narrate(
            f"Ninety-seven point five percent. About four hundred lines. No libraries."
        ) as t:
            final = VGroup(
                mono(f"{acc:.2f}%", size=72, color=GOLD),
                mono("~400 lines of Python", size=30, color=FG),
                mono("no machine learning libraries", size=30, color=MUTED),
            ).arrange(DOWN, buff=0.45)
            final.move_to(UP * 0.4)
            self.play(FadeIn(final[0], scale=0.85), run_time=1.0)
            self.play(
                LaggedStart(FadeIn(final[1]), FadeIn(final[2]), lag_ratio=0.4),
                run_time=1.4,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Every equation in this video is one I typed out and got wrong at least once first."
        ) as t:
            last = body(
                "every equation here is one I got wrong at least once first", 26, MUTED
            )
            last.next_to(final, DOWN, buff=1.0)
            self.play(FadeIn(last, shift=UP * 0.15), run_time=1.2)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.6))

        self.clear_out(run_time=1.6)
        self.wait(0.6)
