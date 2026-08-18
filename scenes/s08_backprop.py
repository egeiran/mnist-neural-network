"""Scene 8 — Backpropagation (5:15–5:55)."""

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
    backdrop,
    body,
    chips,
    mono,
    place_chips,
    run,
)
from scenes.netviz import NetView

EQUATIONS = [
    "delta = (A2 - Y) * sig'(Z2) * 2",
    "dW2   = A1.T @ delta / m",
    "delta = (delta @ W2.T) * sig'(Z1)",
    "dW1   = A0.T @ delta / m",
]


class S08Backprop(NarratedScene):
    def construct(self):
        data = run()
        out = data["untrained_out"]
        target = data["target_onehot"]
        hidden = data["untrained_hidden"]
        pixels = data["demo_image"]
        dW1 = np.abs(data["dW1_init"])
        dW2 = np.abs(data["dW2_init"])

        net = NetView(pixels, hidden, out, x_out=-0.2)
        for c, v in zip(net.hidden, net.hidden_values):
            c.set_fill(ACCENT, opacity=float(np.clip(v, 0.05, 1)))
        for c, v in zip(net.out, net.out_values):
            c.set_fill(ACCENT, opacity=float(np.clip(v, 0.05, 1)))

        skeleton = net.skeleton()

        with self.narrate(
            "So I need the slope. For every weight, how much would the loss change if I "
            "nudged this one thing?"
        ) as t:
            self.play(FadeIn(skeleton), run_time=1.0)
            probe = net.wires1[40]
            highlight = probe.copy().set_stroke(GOLD, width=4, opacity=1)
            q = mono("∂ loss / ∂ w  = ?", size=24, color=GOLD)
            q.next_to(highlight.get_center(), UP, buff=0.35).shift(RIGHT * 0.6)
            q_box = backdrop(q, buff=0.15)
            self.play(Create(highlight), FadeIn(q_box), run_time=1.0)
            self.wait(max(t.get_remaining_duration() - 0.4, 0.1))
            self.play(FadeOut(highlight), FadeOut(q_box), run_time=0.4)

        with self.narrate(
            "A hundred thousand weights, and I need all of them, for every image. That sounds "
            "impossible, and for a long time it basically was."
        ) as t:
            many = mono(f"{int(data['n_weights']):,} parameters", size=26, color=GOLD).to_corner(UR, buff=0.7)
            self.play(FadeIn(many), run_time=0.6)
            self.play(
                net.flash(net.wires1, color=GOLD, run_time=1.2, every=7),
                net.flash(net.wires2, color=GOLD, run_time=1.2, every=5),
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Feilen ved utgangen ---------------------------------------------
        with self.narrate(
            "The trick is called backpropagation. Start at the output, where the error is "
            "obvious — you can see exactly what it got wrong."
        ) as t:
            self.play(FadeOut(many), run_time=0.3)
            err = out - target
            halos = VGroup()
            for c, e in zip(net.out, err):
                halos.add(
                    Circle(
                        radius=0.155 + 0.16 * abs(float(e)),
                        stroke_color=WARM,
                        stroke_width=3,
                        fill_opacity=0,
                    ).move_to(c.get_center())
                )
            err_tag = mono("error", size=22, color=WARM).next_to(net.out, UP, buff=0.3)
            self.play(
                LaggedStart(*[Create(h) for h in halos], lag_ratio=0.07),
                FadeIn(err_tag),
                run_time=1.4,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Feilen flyter bakover -------------------------------------------
        with self.narrate(
            "Then push that error backwards. Each layer hands blame to the layer before it, "
            "weighted by how much each connection contributed. Four equations, one pass "
            "backwards, and you get every gradient at once."
        ) as t:
            eqs = VGroup(*[mono(e, size=20, color=MUTED) for e in EQUATIONS])
            eqs.arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.5)
            eqs.shift(UP * 0.3)

            # bakoverbølge langs lag 2, vekt for vekt
            m2 = dW2 / (dW2.max() + 1e-12)
            back2 = []
            for w, (h_i, o_j) in zip(net.wires2, net.wires2_meta):
                g = float(m2[h_i, o_j])
                rev = Line(w.get_end(), w.get_start(), stroke_color=WARM,
                           stroke_width=0.6 + 3.4 * g, stroke_opacity=0.3 + 0.7 * g)
                back2.append(ShowPassingFlash(rev, time_width=0.5))
            self.play(
                LaggedStart(*back2, lag_ratio=0.004),
                FadeIn(eqs[0], shift=LEFT * 0.2),
                run_time=1.6,
            )
            self.play(
                LaggedStart(
                    *[c.animate.set_stroke(WARM, width=2.5) for c in net.hidden],
                    lag_ratio=0.05,
                ),
                FadeIn(eqs[1], shift=LEFT * 0.2),
                run_time=1.0,
            )

            m1 = dW1 / (dW1.max() + 1e-12)
            back1 = []
            for w, (p_i, h_j) in zip(net.wires1, net.wires1_meta):
                g = float(m1[p_i, h_j])
                rev = Line(w.get_end(), w.get_start(), stroke_color=WARM,
                           stroke_width=0.5 + 3.0 * g, stroke_opacity=0.25 + 0.75 * g)
                back1.append(ShowPassingFlash(rev, time_width=0.5))
            self.play(
                LaggedStart(*back1, lag_ratio=0.006),
                FadeIn(eqs[2], shift=LEFT * 0.2),
                run_time=1.8,
            )
            self.play(
                net.inputs[1].animate.set_stroke(WARM, width=2.5),
                FadeIn(eqs[3], shift=LEFT * 0.2),
                run_time=0.8,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate("That's the whole idea. Blame flows backwards.") as t:
            arrow = Arrow(
                np.array([0.6, -3.45, 0]),
                np.array([-2.6, -3.45, 0]),
                color=WARM,
                stroke_width=6,
                buff=0.0,
            )
            self.play(GrowArrow(arrow), run_time=1.0)
            self.play(FadeIn(place_chips(chips("error flows backwards", color=WARM))), run_time=0.5)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
