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
    signed_rgb,
)

ROWS, COLS, GAP = 8, 16, 2


def weight_sheet(W: np.ndarray) -> np.ndarray:
    """128 nevroner → ett stort bilde, hvert felt normalisert for seg."""
    h = ROWS * 28 + (ROWS - 1) * GAP
    w = COLS * 28 + (COLS - 1) * GAP
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    bg = np.array(ManimColor(BG).to_rgb()) * 255
    canvas[:, :] = bg.astype(np.uint8)
    for k in range(min(W.shape[1], ROWS * COLS)):
        r, c = divmod(k, COLS)
        tile = signed_rgb(W[:, k].reshape(28, 28))
        y, x = r * (28 + GAP), c * (28 + GAP)
        canvas[y : y + 28, x : x + 28] = tile
    return canvas


class S11WhatItLearned(NarratedScene):
    def construct(self):
        data = run()
        W1_init = data["W1_init"]
        W1_final = data["W1_final"]
        acc = float(data["epoch_acc"][-1]) * 100
        worst_imgs = data["worst_images"]
        worst_true = data["worst_true"]
        worst_pred = data["worst_pred"]

        sheet_before = image_from_array(weight_sheet(W1_init), height=5.0)
        sheet_after = image_from_array(weight_sheet(W1_final), height=5.0)
        for m in (sheet_before, sheet_after):
            m.move_to(DOWN * 0.25)

        with self.narrate(
            "Here's what the hidden layer actually learned — each square is one neuron's "
            "weights, drawn back out as an image."
        ) as t:
            caption = mono("128 hidden neurons  ·  784 weights each, folded back to 28 × 28",
                           size=20, color=MUTED)
            caption.next_to(sheet_after, DOWN, buff=0.45)
            stamp = mono("before training", size=24, color=MUTED)
            stamp.next_to(sheet_after, UP, buff=0.4)

            self.play(FadeIn(sheet_before), FadeIn(stamp), run_time=1.0)
            self.play(FadeIn(caption), run_time=0.6)
            self.wait(max(t.get_remaining_duration() - 1.4, 0.2))

            after_stamp = mono("after 10 epochs", size=24, color=ACCENT).move_to(stamp)
            self.play(
                FadeOut(sheet_before),
                FadeIn(sheet_after),
                Transform(stamp, after_stamp),
                run_time=1.2,
            )

        with self.narrate(
            "I was expecting stroke detectors. Clean little edges and curves. That's not what "
            "I got. It's structured noise. The network found something that works, not "
            "something that explains itself. That's worth sitting with."
        ) as t:
            picks = [18, 53, 97]
            tile_w = sheet_after.width / COLS
            tile_h = sheet_after.height / ROWS
            boxes = VGroup()
            for k in picks:
                r, c = divmod(k, COLS)
                center = sheet_after.get_corner(UL) + np.array(
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
                FadeOut(sheet_after), FadeOut(boxes), FadeOut(caption),
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
