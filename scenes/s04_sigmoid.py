"""Scene 4 — Sigmoid, and why (2:35–3:15)."""

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
    backdrop,
    body,
    chips,
    formula,
    mono,
    place_chips,
)


def sig(v):
    return 1 / (1 + np.exp(-v))


def dsig(v):
    return sig(v) * (1 - sig(v))


def mini_panel(slope: float, label: str, width=2.1, height=1.5) -> VGroup:
    """Liten graf-rute som viser en rett linje."""
    frame = Rectangle(width=width, height=height, stroke_color=DIM, stroke_width=2)
    y = np.clip(slope * width / 2, -height / 2 + 0.1, height / 2 - 0.1)
    line = Line(
        frame.get_center() + LEFT * width / 2 + DOWN * y,
        frame.get_center() + RIGHT * width / 2 + UP * y,
        color=MUTED,
        stroke_width=3,
    )
    tag = mono(label, size=18, color=MUTED).next_to(frame, DOWN, buff=0.15)
    return VGroup(frame, line, tag)


class S04Sigmoid(NarratedScene):
    def construct(self):
        axes = Axes(
            x_range=[-8, 8, 2],
            y_range=[0, 1, 0.5],
            x_length=9.0,
            y_length=4.4,
            tips=False,
            axis_config={"color": DIM, "stroke_width": 2},
        )
        axes.move_to(UP * 0.3)
        ticks = axis_ticks(axes, x_vals=(-8, -4, 4, 8), y_vals=(0.5, 1.0), size=18)
        line = axes.plot(lambda v: np.clip(v / 8 + 0.5, 0, 1), color=DIM, stroke_width=3)
        curve = axes.plot(sig, color=ACCENT, stroke_width=5)

        z = ValueTracker(-7.5)
        dot = always_redraw(lambda: Dot(axes.c2p(z.get_value(), sig(z.get_value())), color=GOLD, radius=0.09))
        readout = always_redraw(
            lambda: mono(
                f"z = {z.get_value():+.2f}   σ(z) = {sig(z.get_value()):.3f}",
                size=26,
                color=GOLD,
            ).to_edge(UP, buff=0.45)
        )

        with self.narrate(
            "This is the sigmoid function. Feed it any number, it gives you back something "
            "between zero and one. Big negative goes to zero, big positive goes to one, and "
            "zero goes to exactly a half."
        ) as t:
            self.play(Create(axes), FadeIn(ticks), run_time=1.2)
            self.play(Create(line), run_time=0.6)
            self.play(Transform(line, curve), run_time=1.6)
            self.remove(line)
            self.add(curve)

            eq = place_chips(chips("σ(z) = 1 / (1 + exp(−z))"))
            self.play(FadeIn(eq), run_time=0.5)

            self.add(dot, readout)
            self.play(z.animate.set_value(0), run_time=1.6, rate_func=linear)
            half = DashedLine(axes.c2p(-8, 0.5), axes.c2p(0, 0.5), color=MUTED, stroke_width=2)
            self.play(Create(half), run_time=0.6)
            self.play(z.animate.set_value(7.5), run_time=1.8, rate_func=linear)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "So z is “how much evidence did I gather,” and the output is "
            "“how confident am I, from zero to one.”"
        ) as t:
            x_lab = body("z — how much evidence", 24, MUTED)
            x_lab.next_to(axes, DOWN, buff=0.3).align_to(axes, RIGHT).shift(LEFT * 0.3)
            y_lab = body("confidence", 24, MUTED).rotate(PI / 2)
            y_lab.next_to(axes, LEFT, buff=0.9)
            self.play(FadeIn(x_lab, shift=UP * 0.15), FadeIn(y_lab, shift=RIGHT * 0.15), run_time=1.0)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Hvorfor den må være der --------------------------------------
        with self.narrate(
            "But here's the real reason it's there. Without it, every layer would just be "
            "multiplication and addition — and stacking two of those gives you something you "
            "could have done in one. A hundred layers would be no more powerful than one. "
            "The sigmoid is what makes depth mean anything."
        ) as t:
            others = VGroup(axes, ticks, curve, half, x_lab, y_lab)
            self.remove(dot, readout)
            self.play(FadeOut(others), run_time=0.7)

            p1 = mini_panel(0.5, "layer 1:  × W1")
            p2 = mini_panel(1.1, "layer 2:  × W2")
            p3 = mini_panel(0.8, "one layer:  × W")
            arrow = mono("→", size=34, color=MUTED)
            eqs = mono("=", size=34, color=MUTED)
            panel = VGroup(p1, arrow, p2, eqs, p3).arrange(RIGHT, buff=0.45)
            caption = body("stack two straight lines and you still have a straight line", 24, MUTED)
            caption.next_to(panel, DOWN, buff=0.5)
            block = VGroup(panel, caption)

            self.play(FadeIn(block, shift=UP * 0.2), run_time=1.0)
            self.wait(min(2.2, max(t.get_remaining_duration() - 1.6, 0.3)))

            punch = body("σ is what makes depth mean anything", 28, ACCENT)
            punch.move_to(caption)
            self.play(Transform(caption, punch), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.9, 0.2))
            self.play(FadeOut(block), FadeIn(others), run_time=0.8)

        # --- Metning ---------------------------------------------------------
        with self.narrate(
            "Watch what happens out here, though. When z gets large, the curve goes flat. "
            "Nudging z does nothing. The neuron is saturated, and saturated neurons stop learning."
        ) as t:
            z.set_value(0.0)

            def tangent():
                v = z.get_value()
                s, d = sig(v), dsig(v)
                dx = 2.2
                return Line(
                    axes.c2p(v - dx, s - dx * d),
                    axes.c2p(v + dx, s + dx * d),
                    color=WARM,
                    stroke_width=4,
                )

            tan = always_redraw(tangent)
            slope_txt = always_redraw(
                lambda: mono(f"slope = {dsig(z.get_value()):.4f}", size=26, color=WARM)
                .to_edge(UP, buff=0.45)
            )
            self.add(dot, tan, slope_txt)
            self.play(FadeIn(dot), Create(tan), FadeIn(slope_txt), run_time=0.8)
            self.play(z.animate.set_value(8.0), run_time=3.0, rate_func=smooth)

            flat = axes.plot(sig, x_range=[4, 8], color=WARM, stroke_width=7)
            flat_left = axes.plot(sig, x_range=[-8, -4], color=WARM, stroke_width=7)
            self.play(Create(flat), Create(flat_left), run_time=0.8)
            self.play(
                Flash(axes.c2p(6, sig(6)), color=WARM, line_length=0.4, num_lines=16),
                run_time=0.6,
            )
            self.play(FadeIn(place_chips(chips("flat curve → no learning", color=WARM)).shift(UP * 0.62)), run_time=0.5)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "That's why the pixels get divided by two fifty-five, and why the starting weights "
            "get scaled down — to keep z in the part of the curve that still has a slope."
        ) as t:
            self.remove(tan, slope_txt)
            good = axes.plot(sig, x_range=[-2.5, 2.5], color=GREEN, stroke_width=8)
            band = Rectangle(
                width=axes.c2p(2.5, 0)[0] - axes.c2p(-2.5, 0)[0],
                height=4.4,
                stroke_width=0,
                fill_color=GREEN,
                fill_opacity=0.08,
            ).move_to(axes.c2p(0, 0.5))
            keep = body("keep z in here", 24, GREEN).next_to(band, UP, buff=0.1)
            self.play(FadeIn(band), Create(good), FadeIn(keep), run_time=1.2)
            self.play(z.animate.set_value(0.6), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
