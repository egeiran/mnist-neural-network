"""Scene 3 — One neuron (1:25–2:35)."""

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
    axis_ticks,
    backdrop,
    body,
    chips,
    mono,
    neuron,
    place_chips,
)

XS = np.array([0.00, 0.83, 1.00, 0.21])
WS = np.array([1.4, -0.9, 2.6, 1.8])
B = 0.5


class S03OneNeuron(NarratedScene):
    def construct(self):
        products = XS * WS
        s = float(products.sum())
        z = s + B
        a = 1 / (1 + np.exp(-z))

        # --- Oppsett ------------------------------------------------------
        inputs = VGroup()
        for i, x in enumerate(XS):
            c = Circle(radius=0.36, stroke_color=MUTED, stroke_width=2,
                       fill_color=WHITE, fill_opacity=float(x))
            val = mono(f"{x:.2f}", size=19, color=FG if x < 0.5 else BLACK)
            val.move_to(c.get_center())
            inputs.add(VGroup(c, val))
        inputs.arrange(DOWN, buff=0.88).move_to(LEFT * 5.3 + DOWN * 0.25)

        in_labels = VGroup()
        for i, g in enumerate(inputs):
            lbl = mono(f"x{i + 1}", size=22, color=MUTED).next_to(g, LEFT, buff=0.25)
            in_labels.add(lbl)

        cell = neuron(radius=0.66, value=0.0)
        cell.set_stroke(MUTED, width=2.5).move_to(LEFT * 1.1)

        arrows = VGroup()
        w_labels = VGroup()
        for g, w in zip(inputs, WS):
            arr = Arrow(
                g[0].get_right(),
                cell.get_left(),
                buff=0.12,
                stroke_width=2 + 2.2 * abs(w),
                max_tip_length_to_length_ratio=0.05,
                color=ACCENT if w > 0 else WARM,
            )
            arrows.add(arr)
            lab = mono(f"{w:+.1f}", size=21, color=ACCENT if w > 0 else WARM)
            lab.move_to(arr.point_from_proportion(0.42) + UP * 0.28 + LEFT * 0.05)
            w_labels.add(lab)

        with self.narrate("Here's the piece everything is built from. One neuron.") as t:
            self.play(GrowFromCenter(cell), run_time=0.9)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "A neuron looks at its inputs and asks one question. Something like: is there a "
            "horizontal stroke near the top of this image?"
        ) as t:
            question = body("“is there a stroke near the top?”", 28, MUTED)
            question.next_to(cell, UP, buff=1.5)
            self.play(FadeIn(question, shift=DOWN * 0.2), run_time=0.8)
            self.play(
                LaggedStart(*[FadeIn(g, shift=RIGHT * 0.2) for g in inputs], lag_ratio=0.15),
                FadeIn(in_labels),
                run_time=1.4,
            )
            self.play(LaggedStart(*[GrowArrow(ar) for ar in arrows], lag_ratio=0.15), run_time=1.4)
            note = body("(showing 4 inputs — the real thing has 784)", 22, DIM)
            note.to_edge(DOWN, buff=0.42).shift(RIGHT * 2.6)
            self.play(FadeIn(note), run_time=0.5)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "It answers by voting. Every input gets a weight. Positive weight means "
            "“I want brightness here.” Negative means “I want darkness here.” "
            "Zero means “I don't care.” Multiply each input by its weight, add them all up, "
            "and add one more number called the bias — that's the threshold, how much evidence "
            "this neuron needs before it speaks up."
        ) as t:
            self.play(FadeOut(question), run_time=0.4)
            self.play(
                LaggedStart(*[FadeIn(w, scale=0.6) for w in w_labels], lag_ratio=0.2),
                run_time=1.4,
            )

            legend = VGroup(
                mono("+  wants brightness", size=20, color=ACCENT),
                mono("−  wants darkness", size=20, color=WARM),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            legend.to_corner(UR, buff=0.6)
            self.play(FadeIn(legend), run_time=0.6)

            # Produktene dukker opp langs pilene
            prods = VGroup()
            for arr, x, w, p in zip(arrows, XS, WS, products):
                txt = mono(f"{x:.2f}×{w:+.1f} = {p:+.2f}", size=19, color=GOLD)
                txt.move_to(arr.point_from_proportion(0.78) + DOWN * 0.3)
                prods.add(txt)
            self.play(
                LaggedStart(*[FadeIn(p, scale=0.7) for p in prods], lag_ratio=0.18),
                run_time=1.8,
            )

            # ... og glir sammen til en sum
            row_y = cell.get_center()[1] - 2.75
            row_x = -4.3
            self.play(
                LaggedStart(
                    *[
                        Transform(
                            p,
                            mono(f"{v:+.2f}", size=28, color=GOLD).move_to(
                                np.array([row_x + i * 1.28, row_y, 0])
                            ),
                        )
                        for i, (p, v) in enumerate(zip(prods, products))
                    ],
                    lag_ratio=0.1,
                ),
                run_time=1.4,
            )
            total = mono(f"=  {s:.2f}", size=28, color=GOLD)
            total.next_to(prods, RIGHT, buff=0.4)
            self.play(FadeIn(total, shift=LEFT * 0.2), run_time=0.7)

            bias = mono(f"+ bias {B:+.1f}", size=26, color=VIOLET)
            bias.next_to(total, RIGHT, buff=0.4)
            self.play(FadeIn(bias, shift=UP * 0.25), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "What comes out is one number. I call it z. It can be anything — minus twelve, "
            "zero point three, forty-seven."
        ) as t:
            z_text = mono(f"z = {z:.2f}", size=44, color=GOLD)
            z_text.next_to(cell, UP, buff=0.75)
            self.play(
                ReplacementTransform(VGroup(prods, total, bias), z_text),
                FadeOut(legend),
                run_time=1.3,
            )
            eq = place_chips(chips("z = w1·x1 + w2·x2 + ... + b"))
            self.play(FadeIn(backdrop(eq)), run_time=0.6)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Sigmoid glir inn fra siden --------------------------------------
        with self.narrate("And then I squash it.") as t:
            axes = Axes(
                x_range=[-6, 6, 3],
                y_range=[0, 1, 0.5],
                x_length=4.6,
                y_length=2.4,
                tips=False,
                axis_config={"color": DIM, "stroke_width": 2},
            )
            axes.move_to(RIGHT * 3.6)
            curve = axes.plot(lambda v: 1 / (1 + np.exp(-v)), color=ACCENT, stroke_width=4)
            ticks = axis_ticks(axes, x_vals=(-6, -3, 6), y_vals=(0.5,), size=16)
            sig_label = mono("σ(z)", size=24, color=ACCENT).next_to(axes, UP, buff=0.2)
            group = VGroup(axes, curve, ticks, sig_label)
            group.shift(RIGHT * 6)
            self.add(group)
            self.play(group.animate.shift(LEFT * 6), run_time=1.0)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Two point seven three goes in. Nought point nine four comes out — this neuron is "
            "fairly sure the answer to its question is yes."
        ) as t:
            dot = Dot(axes.c2p(z, 0), color=GOLD, radius=0.07)
            z_tag = mono(f"{z:.2f}", size=20, color=GOLD).next_to(dot, DOWN, buff=0.12)
            self.play(FadeIn(dot), FadeIn(z_tag), run_time=0.5)
            self.play(dot.animate.move_to(axes.c2p(z, a)), run_time=1.0)

            hline = DashedLine(axes.c2p(z, a), axes.c2p(-6, a), color=GOLD, stroke_width=2)
            out_tag = mono(f"{a:.2f}", size=22, color=GOLD).next_to(axes.c2p(-6, a), LEFT, buff=0.15)
            self.play(Create(hline), FadeIn(out_tag), run_time=0.8)

            fill = mono(f"{a:.2f}", size=22, color=BLACK).move_to(cell.get_center())
            self.play(
                cell.animate.set_fill(ACCENT, opacity=float(a)),
                FadeIn(fill),
                Flash(cell, color=ACCENT, line_length=0.25, num_lines=14),
                run_time=1.2,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
