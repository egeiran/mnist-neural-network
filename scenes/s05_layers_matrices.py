"""Scene 5 — Layers and matrices (3:15–3:55)."""

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
    VIOLET,
    WARM,
    backdrop,
    body,
    chips,
    image_from_array,
    mono,
    neuron,
    place_chips,
    run,
    signed_rgb,
)

rng = np.random.default_rng(7)


def block(w: float, h: float, label: str, dims: str, color: str) -> VGroup:
    rect = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2.5,
                     fill_color=color, fill_opacity=0.10)
    name = mono(label, size=26, color=color).move_to(rect.get_center())
    dim = mono(dims, size=19, color=MUTED).next_to(rect, DOWN, buff=0.18)
    return VGroup(rect, name, dim)


class S05LayersMatrices(NarratedScene):
    def construct(self):
        data = run()
        W1 = data["W1_final"]

        # --- 784 inn i ett nevron --------------------------------------------
        col_h, col_w = 4.6, 0.34
        vec = data["showcase_images"][0].reshape(-1)
        slivers = VGroup()
        for i, v in enumerate(vec):
            slivers.add(
                Rectangle(
                    width=col_w,
                    height=col_h / 784,
                    fill_color=WHITE,
                    fill_opacity=float(np.clip(v, 0, 1)),
                    stroke_width=0,
                ).move_to(np.array([-5.6, col_h / 2 - (i + 0.5) * col_h / 784, 0]))
            )
        col_frame = SurroundingRectangle(slivers, color=DIM, stroke_width=2, buff=0.05)
        col_tag = mono("784", size=22, color=MUTED).next_to(col_frame, DOWN, buff=0.2)
        column = VGroup(slivers, col_frame, col_tag)

        one = neuron(radius=0.3, value=0.72)
        one.move_to(RIGHT * 0.2)

        def fan(target, n=26, width=1.0):
            g = VGroup()
            ys = np.linspace(-col_h / 2, col_h / 2, n)
            for y in ys:
                g.add(
                    Line(
                        np.array([-5.6 + col_w / 2, y, 0]),
                        target.get_left(),
                        stroke_width=width,
                        stroke_color=ACCENT,
                        stroke_opacity=0.5,
                    )
                )
            return g

        with self.narrate(
            "One neuron asks one question. A layer is a hundred and twenty-eight neurons asking "
            "a hundred and twenty-eight different questions at the same time."
        ) as t:
            self.play(FadeIn(column), run_time=0.8)
            self.play(GrowFromCenter(one), run_time=0.5)
            wires = fan(one)
            self.play(Create(wires), run_time=1.0)

            # ... og så 128 av dem
            cells = VGroup(*[neuron(radius=0.12, value=float(v)) for v in rng.random(16)])
            cells.arrange(DOWN, buff=0.15).move_to(RIGHT * 0.2)
            brace = Brace(cells, RIGHT, color=MUTED)
            brace_tag = mono("128 neurons", size=22, color=MUTED).next_to(brace, RIGHT, buff=0.18)

            all_wires = VGroup()
            for c in cells:
                all_wires.add(*fan(c, n=7, width=0.5))

            self.play(
                ReplacementTransform(one, cells),
                ReplacementTransform(wires, all_wires),
                run_time=1.6,
            )
            self.play(GrowFromCenter(brace), FadeIn(brace_tag), run_time=0.6)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Floken blir en matrise ------------------------------------------
        with self.narrate(
            "Each one has its own seven hundred and eighty-four weights, so I stack them into "
            "a grid — a matrix. Seven eighty-four by one twenty-eight."
        ) as t:
            w_img = image_from_array(signed_rgb(W1), height=col_h)
            w_img.stretch_to_fit_width(2.3)
            w_img.move_to(RIGHT * 1.4)
            w_frame = SurroundingRectangle(w_img, color=DIM, stroke_width=2, buff=0.0)
            w_tag = VGroup(
                mono("W1", size=26, color=FG),
                mono("784 × 128", size=20, color=MUTED),
            ).arrange(DOWN, buff=0.12).next_to(w_frame, DOWN, buff=0.25)

            self.play(
                FadeOut(all_wires, shift=RIGHT * 0.4),
                FadeOut(cells),
                FadeOut(brace),
                FadeOut(brace_tag),
                run_time=0.8,
            )
            self.play(FadeIn(w_img, scale=0.92), Create(w_frame), FadeIn(w_tag), run_time=1.2)

            legend = VGroup(
                mono("blue  = positive weight", size=19, color=ACCENT),
                mono("red   = negative weight", size=19, color=WARM),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).to_corner(UR, buff=0.6)
            self.play(FadeIn(legend), run_time=0.5)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Hele laget på én linje kode --------------------------------------
        with self.narrate(
            "And now the whole layer is one line of code. Inputs times weights, plus bias. "
            "That's not new math, it's just bookkeeping. The matrix multiply does a hundred "
            "thousand multiply-and-adds in a single operation, and it does it for thirty-two "
            "images at once."
        ) as t:
            self.play(
                FadeOut(column), FadeOut(w_img), FadeOut(w_frame), FadeOut(w_tag), FadeOut(legend),
                run_time=0.7,
            )

            X = block(1.5, 2.4, "X", "32 × 784", GOLD)
            at = mono("@", size=34, color=MUTED)
            W = block(2.4, 2.4, "W", "784 × 128", ACCENT)
            plus = mono("+", size=34, color=MUTED)
            b = block(0.55, 2.4, "b", "128", VIOLET)
            eq = mono("=", size=34, color=MUTED)
            Z = block(2.4, 2.4, "Z", "32 × 128", GREEN)
            row = VGroup(X, at, W, plus, b, eq, Z).arrange(RIGHT, buff=0.4)
            row.move_to(UP * 0.35)

            code = mono("Z = X @ W + b", size=36, color=FG).next_to(row, DOWN, buff=0.9)

            self.play(
                LaggedStart(
                    FadeIn(X, shift=UP * 0.2),
                    FadeIn(at),
                    FadeIn(W, shift=UP * 0.2),
                    FadeIn(plus),
                    FadeIn(b, shift=UP * 0.2),
                    lag_ratio=0.25,
                ),
                run_time=1.8,
            )
            self.play(FadeIn(eq), FadeIn(Z, shift=LEFT * 0.3), run_time=0.9)
            self.play(FadeIn(code, shift=UP * 0.15), run_time=0.7)

            counter = mono("100,352 multiply-and-adds  ·  32 images at a time", size=22, color=MUTED)
            counter.next_to(code, DOWN, buff=0.45)
            self.play(FadeIn(counter), run_time=0.6)
            self.play(Indicate(W[0], color=ACCENT, scale_factor=1.05), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Andre lag --------------------------------------------------------
        with self.narrate(
            "Then a second layer takes those hundred and twenty-eight answers down to ten. "
            "One output per digit."
        ) as t:
            self.play(
                FadeOut(VGroup(row, code, counter)),
                run_time=0.6,
            )

            n1 = block(1.05, 3.2, "784", "input", MUTED)
            a1 = mono("@ W1 →", size=24, color=ACCENT)
            n2 = block(1.05, 2.1, "128", "hidden", ACCENT)
            a2 = mono("@ W2 →", size=24, color=GREEN)
            n3 = block(1.05, 1.0, "10", "output", GREEN)
            pipe = VGroup(n1, a1, n2, a2, n3).arrange(RIGHT, buff=0.7)
            pipe.move_to(UP * 0.2)

            self.play(
                LaggedStart(
                    FadeIn(n1), FadeIn(a1), FadeIn(n2), FadeIn(a2), FadeIn(n3),
                    lag_ratio=0.3,
                ),
                run_time=2.0,
            )
            self.play(FadeIn(place_chips(chips("784 → 128 → 10", color=GREEN))), run_time=0.5)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
