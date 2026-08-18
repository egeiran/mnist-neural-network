"""Scene 10 — Training (6:20–6:50)."""

import numpy as np
from manim import *

from scenes.common import (
    ACCENT,
    DIM,
    FG,
    GOLD,
    GREEN,
    MUTED,
    NarratedScene,
    WARM,
    axis_ticks,
    body,
    chips,
    mono,
    place_chips,
    run,
)

EPOCHS = 10
PER_EPOCH = 40  # punkter i losskurven per epoke


def smooth_losses(batch_losses: np.ndarray) -> np.ndarray:
    """Glatt batch-tapet og sampl ned til PER_EPOCH punkter per epoke."""
    w = 40
    kernel = np.ones(w) / w
    padded = np.concatenate([np.full(w - 1, batch_losses[0]), batch_losses])
    smoothed = np.convolve(padded, kernel, mode="valid")
    n = EPOCHS * PER_EPOCH
    idx = np.linspace(0, len(smoothed) - 1, n).astype(int)
    return smoothed[idx]


class S10Training(NarratedScene):
    def construct(self):
        data = run()
        acc = np.array(data["epoch_acc"]) * 100
        curve_y = smooth_losses(np.array(data["batch_losses"]))
        curve_x = np.linspace(0, EPOCHS, len(curve_y))

        loss_axes = Axes(
            x_range=[0, 10, 2],
            y_range=[-2, 1, 1],
            x_length=5.4,
            y_length=3.3,
            tips=False,
            axis_config={"color": DIM, "stroke_width": 2},
            y_axis_config={"scaling": LogBase(10)},
        )
        loss_axes.move_to(LEFT * 3.5 + DOWN * 0.4)
        loss_ticks = VGroup(
            *[
                mono(f"{v:g}", 17, MUTED).next_to(loss_axes.c2p(0, v), LEFT, buff=0.15)
                for v in (0.01, 0.1, 1.0)
            ],
            *[
                mono(str(v), 17, MUTED).next_to(loss_axes.c2p(v, 0.01), DOWN, buff=0.15)
                for v in (2, 4, 6, 8, 10)
            ],
        )
        loss_title = body("loss", 26, GOLD).next_to(loss_axes, UP, buff=0.35)

        acc_axes = Axes(
            x_range=[0, 10, 2],
            y_range=[90, 100, 2],
            x_length=5.4,
            y_length=3.3,
            tips=False,
            axis_config={"color": DIM, "stroke_width": 2},
        )
        acc_axes.move_to(RIGHT * 3.5 + DOWN * 0.4)
        acc_ticks = VGroup(
            *[
                mono(f"{v}%", 17, MUTED).next_to(acc_axes.c2p(0, v), LEFT, buff=0.15)
                for v in (92, 94, 96, 98)
            ],
            *[
                mono(str(v), 17, MUTED).next_to(acc_axes.c2p(v, 90), DOWN, buff=0.15)
                for v in (2, 4, 6, 8, 10)
            ],
        )
        acc_title = body("accuracy", 26, GREEN).next_to(acc_axes, UP, buff=0.35)
        epoch_lab = body("epochs", 20, MUTED).next_to(acc_axes, DOWN, buff=0.55)

        with self.narrate(
            "Then it's just: show it thirty-two images, measure the error, nudge every weight "
            "downhill, repeat. Eighteen hundred and seventy-five times per pass through the "
            "data. Ten passes."
        ) as t:
            loop = VGroup(
                mono("for each batch of 32:", size=24, color=FG),
                mono("    forward  →  loss", size=24, color=MUTED),
                mono("    backward →  gradients", size=24, color=MUTED),
                mono("    W -= lr * dW", size=24, color=MUTED),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
            self.play(
                LaggedStart(*[FadeIn(l, shift=RIGHT * 0.2) for l in loop], lag_ratio=0.3),
                run_time=2.0,
            )
            count = mono("1,875 batches × 10 epochs", size=24, color=GOLD)
            count.next_to(loop, DOWN, buff=0.6)
            self.play(FadeIn(count), run_time=0.7)
            self.wait(max(t.get_remaining_duration() - 0.6, 0.2))
            self.play(FadeOut(loop), FadeOut(count), run_time=0.5)

        with self.narrate(
            "After one pass it was already at ninety-three percent. After ten, ninety-seven "
            "point five."
        ) as t:
            self.play(
                Create(loss_axes), Create(acc_axes),
                FadeIn(loss_ticks), FadeIn(acc_ticks),
                FadeIn(loss_title), FadeIn(acc_title),
                FadeIn(epoch_lab),
                run_time=1.4,
            )

            counter = mono("epoch 0 / 10", size=26, color=FG).to_edge(UP, buff=0.45)
            self.add(counter)

            prev_acc_pt = acc_axes.c2p(0, 90.0)
            for e in range(EPOCHS):
                lo = max(e * PER_EPOCH - 1, 0)
                hi = (e + 1) * PER_EPOCH
                seg = VMobject(color=GOLD, stroke_width=4)
                seg.set_points_smoothly(
                    [loss_axes.c2p(x, y) for x, y in zip(curve_x[lo:hi], curve_y[lo:hi])]
                )

                pt = acc_axes.c2p(e + 1, acc[e])
                acc_seg = Line(prev_acc_pt, pt, color=GREEN, stroke_width=4)
                dot = Dot(pt, color=GREEN, radius=0.06)
                prev_acc_pt = pt

                new_counter = mono(f"epoch {e + 1} / 10", size=26, color=FG).to_edge(UP, buff=0.45)
                self.play(
                    Create(seg),
                    Create(acc_seg),
                    FadeIn(dot, scale=0.5),
                    Transform(counter, new_counter),
                    run_time=0.55,
                    rate_func=linear,
                )

            first = mono(f"{acc[0]:.2f}%", size=20, color=GREEN)
            first.next_to(acc_axes.c2p(1, acc[0]), DOWN + RIGHT, buff=0.1)
            last = mono(f"{acc[-1]:.2f}%", size=22, color=GREEN)
            last.next_to(acc_axes.c2p(10, acc[-1]), UP, buff=0.2).shift(LEFT * 0.35)
            self.play(FadeIn(first), FadeIn(last), run_time=0.8)
            self.play(
                FadeIn(place_chips(chips(f"epoch 1  — {acc[0]:.2f}%", f"epoch 10 — {acc[-1]:.2f}%"))),
                run_time=0.6,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Loss went down every single epoch, and accuracy climbed almost all the way — "
            "one small wobble near the end. No blow-ups, no plateau. That smoothness is what "
            "correct backprop looks like."
        ) as t:
            down = Arrow(
                loss_axes.c2p(5.2, 1.7), loss_axes.c2p(9.0, 0.28),
                color=GOLD, stroke_width=3, buff=0.05,
                max_tip_length_to_length_ratio=0.12,
            )
            up = Arrow(
                acc_axes.c2p(4.6, 90.7), acc_axes.c2p(9.2, 93.6),
                color=GREEN, stroke_width=3, buff=0.05,
                max_tip_length_to_length_ratio=0.12,
            )
            self.play(GrowArrow(down), GrowArrow(up), run_time=1.2)
            punch = body("no blow-ups, no plateau", 26, FG)
            punch.to_edge(DOWN, buff=0.5).shift(RIGHT * 1.6)
            self.play(FadeIn(punch), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
