"""Delt nettverkstegning for scene 6 (forover) og scene 8 (bakover)."""

from __future__ import annotations

import numpy as np
from manim import *

from scenes.common import ACCENT, DIM, MUTED, mono, neuron, node_column


class NetView:
    """784-kolonne → et utvalg av de 128 skjulte nevronene → 10 utganger."""

    def __init__(
        self,
        pixels: np.ndarray,
        hidden: np.ndarray,
        out: np.ndarray,
        x_in: float = -5.6,
        x_hidden: float = -2.1,
        x_out: float = 0.7,
        col_h: float = 4.2,
    ):
        self.x_in, self.x_hidden, self.x_out = x_in, x_hidden, x_out

        self.in_col = node_column(pixels, radius=0.1, buff=0.13, height=col_h)
        self.in_col.move_to(np.array([x_in, 0, 0]))
        self.in_frame = SurroundingRectangle(self.in_col, color=DIM, stroke_width=2, buff=0.2)
        self.in_tag = mono("784", size=19, color=MUTED).next_to(self.in_frame, DOWN, buff=0.18)
        self.inputs = VGroup(self.in_col, self.in_frame, self.in_tag)

        # Samme grep som på inngangen: noen av de 128, ⋮, noen til. Nodene
        # tegnes tomme og tennes av light_hidden når signalet kommer.
        self.hidden = node_column(
            hidden, n_top=5, n_mid=4, n_bottom=4,
            radius=0.115, buff=0.135, color=ACCENT, fill=False,
        )
        self.hidden.move_to(np.array([x_hidden, 0, 0]))
        self.hidden_values = self.hidden.values
        self.hidden_tag = mono("128", size=19, color=MUTED).next_to(self.hidden, DOWN, buff=0.22)

        self.out = VGroup(*[neuron(radius=0.155, value=0.0) for _ in out])
        self.out.arrange(DOWN, buff=0.26).move_to(np.array([x_out, 0, 0]))
        self.out_values = out
        self.digit_tags = VGroup(
            *[
                mono(str(i), size=19, color=MUTED).next_to(c, LEFT, buff=0.16)
                for i, c in enumerate(self.out)
            ]
        )

        self.hidden_idx = self.hidden.indices
        self.wires1 = VGroup()
        self.wires1_meta = []   # (pikselindeks, skjult indeks) for hver ledning
        # Ledningene går ut fra de nodene vi faktisk viser, så gradientfargen i
        # scene 8 hører til den pikselen ledningen kommer fra.
        for k, c in enumerate(self.hidden.nodes):
            for node, pi in zip(self.in_col.nodes, self.in_col.indices):
                self.wires1_meta.append((int(pi), int(self.hidden_idx[k])))
                self.wires1.add(
                    Line(
                        node.get_right() + RIGHT * 0.02,
                        c.get_left(),
                        stroke_width=0.5,
                        stroke_color=ACCENT,
                        stroke_opacity=0.35,
                    )
                )

        self.wires2 = VGroup()
        self.wires2_meta = []   # (skjult indeks, utgangsindeks)
        for k, c1 in enumerate(self.hidden.nodes):
            for j, c2 in enumerate(self.out):
                self.wires2_meta.append((int(self.hidden_idx[k]), j))
                self.wires2.add(
                    Line(
                        c1.get_right(),
                        c2.get_left(),
                        stroke_width=0.6,
                        stroke_color=ACCENT,
                        stroke_opacity=0.3,
                    )
                )

    def skeleton(self) -> VGroup:
        return VGroup(self.inputs, self.wires1, self.hidden, self.hidden_tag,
                      self.wires2, self.out, self.digit_tags)

    def flash(self, wires: VGroup, color=ACCENT, run_time=1.2, every=3) -> AnimationGroup:
        """Aktiveringsbølge langs et utvalg av ledningene."""
        picks = [w for i, w in enumerate(wires) if i % every == 0]
        return LaggedStart(
            *[
                ShowPassingFlash(
                    w.copy().set_stroke(color, width=2.5, opacity=1.0), time_width=0.6
                )
                for w in picks
            ],
            lag_ratio=0.6 / max(len(picks), 1),
            run_time=run_time,
        )

    def light_hidden(self, run_time=0.9) -> AnimationGroup:
        return LaggedStart(
            *[
                c.animate.set_fill(ACCENT, opacity=float(np.clip(v, 0.05, 1)))
                for c, v in zip(self.hidden.nodes, self.hidden_values)
            ],
            lag_ratio=0.05,
            run_time=run_time,
        )

    def light_out(self, run_time=0.9) -> AnimationGroup:
        return LaggedStart(
            *[
                c.animate.set_fill(ACCENT, opacity=float(np.clip(v, 0.05, 1)))
                for c, v in zip(self.out, self.out_values)
            ],
            lag_ratio=0.06,
            run_time=run_time,
        )
