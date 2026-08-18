"""Scene 9 — Was it right? (5:55–6:20)."""

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
    body,
    chips,
    mono,
    place_chips,
    run,
)
from scenes.s08_backprop import EQUATIONS


def terminal(lines, width=7.4, size=15):
    bar = Rectangle(width=width, height=0.32, fill_color="#161b22", fill_opacity=1,
                    stroke_color=DIM, stroke_width=1.5)
    dots = VGroup(*[Dot(radius=0.045, color=c) for c in ("#ff5f56", "#ffbd2e", "#27c93f")])
    dots.arrange(RIGHT, buff=0.09).next_to(bar.get_left(), RIGHT, buff=0.16)
    text = VGroup(*[mono(l, size=size, color=FG) for l in lines])
    text.arrange(DOWN, aligned_edge=LEFT, buff=0.19)
    body_rect = Rectangle(
        width=width,
        height=text.height + 0.6,
        fill_color="#0b0f14",
        fill_opacity=1,
        stroke_color=DIM,
        stroke_width=1.5,
    )
    bar.next_to(body_rect, UP, buff=0)
    dots.align_to(bar, LEFT).shift(RIGHT * 0.16).set_y(bar.get_y())
    text.move_to(body_rect).align_to(body_rect, LEFT).shift(RIGHT * 0.3)
    return VGroup(body_rect, bar, dots, text), text


class S09GradCheck(NarratedScene):
    def construct(self):
        data = run()
        vals = data["gradcheck_values"]
        idx = data["gradcheck_index"].astype(int)

        rows = [
            f"W[{l}][{i},{j}]   num={num: .8f}   ana={ana: .8f}   rel={rel:.1e}"
            for (l, i, j), (num, ana, rel) in zip(idx, vals)
        ]

        eqs = VGroup(*[mono(e, size=20, color=MUTED) for e in EQUATIONS])
        eqs.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        title = body("the four equations I typed myself", 26, FG).next_to(eqs, UP, buff=0.5)
        left = VGroup(title, eqs).move_to(ORIGIN)

        with self.narrate(
            "Now, I wrote those four equations myself, and there was no way to know if I'd got "
            "them right. Gradients with a bug in them still have the correct shape. They just "
            "quietly point the wrong way."
        ) as t:
            self.play(FadeIn(title), run_time=0.6)
            self.play(
                LaggedStart(*[FadeIn(e, shift=UP * 0.15) for e in eqs], lag_ratio=0.25),
                run_time=1.8,
            )
            warn = body("right shape · wrong direction", 24, WARM).next_to(eqs, DOWN, buff=0.6)
            self.play(FadeIn(warn), run_time=0.7)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))
            self.play(FadeOut(warn), run_time=0.4)

        with self.narrate(
            "So I checked them the slow way. Take one weight, nudge it up a hair, measure the "
            "loss. Nudge it down, measure again. Divide by how far I moved it — that's the "
            "slope, straight from the definition. Painfully slow, but I only needed a handful."
        ) as t:
            self.play(
                left.animate.to_edge(LEFT, buff=0.45).shift(UP * 0.95),
                run_time=1.0,
            )

            definition = VGroup(
                mono("slope ≈  ( loss(w + ε) − loss(w − ε) )  /  2ε", size=22, color=GOLD),
                mono("ε = 1e-5", size=19, color=MUTED),
            ).arrange(DOWN, buff=0.25)
            definition.to_edge(RIGHT, buff=0.6).shift(UP * 2.7)
            self.play(FadeIn(definition[0], shift=UP * 0.2), run_time=0.9)
            self.play(FadeIn(definition[1]), run_time=0.4)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "The two methods agreed to ten decimal places. That's the moment I knew the math "
            "was right."
        ) as t:
            term, text = terminal(
                ["$ python -m nn.network", "gradient check:"] + rows, width=6.9, size=14
            )
            term.to_edge(RIGHT, buff=0.4).shift(DOWN * 0.95)
            self.play(FadeIn(term[0]), FadeIn(term[1]), FadeIn(term[2]), run_time=0.6)
            self.play(
                LaggedStart(*[AddTextLetterByLetter(l, run_time=0.5) for l in text], lag_ratio=0.5),
                run_time=2.6,
            )

            rel_rows = VGroup(*[l for l in text[2:]])
            rel_box = Rectangle(
                width=1.95,
                height=rel_rows.height + 0.2,
                color=GREEN,
                stroke_width=2,
            )
            rel_box.move_to(rel_rows).align_to(rel_rows, RIGHT).shift(RIGHT * 0.07)
            agree = mono("agreed to 10 decimal places", size=19, color=GREEN)
            agree.next_to(term, UP, buff=0.18).align_to(term, RIGHT)
            self.play(Create(rel_box), FadeIn(agree), run_time=1.0)

            self.play(
                FadeIn(
                    place_chips(
                        chips(
                            f"numerical:  {vals[0][0]: .8f}",
                            f"analytical: {vals[0][1]: .8f}",
                            f"rel. error: {vals[0][2]:.1e} ✓",
                        )
                    )
                ),
                run_time=0.7,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.3))

        self.clear_out()
