"""Scene 6 — Forward pass and loss (3:55–4:35)."""

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
from scenes.netviz import NetView

ROW_DY = 0.42
TOP_Y = 1.95


class S06ForwardLoss(NarratedScene):
    def construct(self):
        data = run()
        out = data["untrained_out"]
        target = data["target_onehot"]
        hidden = data["untrained_hidden"]
        pixels = data["demo_image"]
        loss_val = float(data["untrained_loss"])

        net = NetView(pixels, hidden, out)

        with self.narrate(
            "Push an image through both layers and you get ten numbers out. "
            "How strongly the network believes in each digit."
        ) as t:
            self.play(FadeIn(net.inputs), run_time=0.6)
            self.play(
                FadeIn(net.wires1), FadeIn(net.hidden), FadeIn(net.hidden_tag),
                FadeIn(net.wires2), FadeIn(net.out), FadeIn(net.digit_tags),
                run_time=1.0,
            )
            self.play(net.flash(net.wires1, run_time=1.1))
            self.play(net.light_hidden(0.8))
            self.play(net.flash(net.wires2, run_time=1.0, every=2))
            self.play(net.light_out(0.8))
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Tallene ut ------------------------------------------------------
        def column(values, x, fmt="{:.2f}", color=FG, size=19):
            g = VGroup()
            for i, v in enumerate(values):
                g.add(mono(fmt.format(v), size=size, color=color)
                      .move_to(np.array([x, TOP_Y - i * ROW_DY, 0])))
            return g

        x_out, x_tgt, x_diff = 2.0, 3.9, 5.8

        with self.narrate("Untrained, they're all about a half. It has no idea.") as t:
            # nevronene flytter seg inn i tabell-linjene
            self.play(
                *[
                    c.animate.move_to(np.array([0.9, TOP_Y - i * ROW_DY, 0])).scale(0.85)
                    for i, c in enumerate(net.out)
                ],
                *[
                    d.animate.move_to(np.array([0.35, TOP_Y - i * ROW_DY, 0]))
                    for i, d in enumerate(net.digit_tags)
                ],
                FadeOut(net.wires2),
                run_time=1.0,
            )
            out_col = column(out, x_out, color=ACCENT)
            head_out = mono("output", size=19, color=MUTED).move_to(np.array([x_out, TOP_Y + 0.6, 0]))
            self.play(
                LaggedStart(*[FadeIn(v, shift=LEFT * 0.15) for v in out_col], lag_ratio=0.06),
                FadeIn(head_out),
                run_time=1.4,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "To fix that I need to measure how wrong it is. The correct answer for a five is "
            "this — a one in slot five, zeros everywhere else."
        ) as t:
            tgt_col = column(target, x_tgt, fmt="{:.0f}", color=GREEN)
            head_tgt = mono("target", size=19, color=MUTED).move_to(np.array([x_tgt, TOP_Y + 0.6, 0]))
            self.play(
                LaggedStart(*[FadeIn(v, shift=LEFT * 0.15) for v in tgt_col], lag_ratio=0.06),
                FadeIn(head_tgt),
                run_time=1.2,
            )
            box = SurroundingRectangle(
                VGroup(net.digit_tags[5], net.out[5], out_col[5], tgt_col[5]),
                color=GREEN, stroke_width=2, buff=0.12,
            )
            self.play(Create(box), run_time=0.7)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Subtract, square each difference so the negatives don't cancel, add them up. "
            "One number. The loss."
        ) as t:
            diffs = (out - target) ** 2
            diff_col = column(diffs, x_diff, color=GOLD)
            head_diff = mono("(diff)²", size=19, color=MUTED).move_to(np.array([x_diff, TOP_Y + 0.6, 0]))
            self.play(FadeOut(box), run_time=0.3)
            self.play(
                LaggedStart(*[FadeIn(v, shift=LEFT * 0.15) for v in diff_col], lag_ratio=0.06),
                FadeIn(head_diff),
                run_time=1.4,
            )

            rule = Line(
                np.array([x_diff - 0.55, TOP_Y - 9.55 * ROW_DY, 0]),
                np.array([x_diff + 0.55, TOP_Y - 9.55 * ROW_DY, 0]),
                color=MUTED, stroke_width=2,
            )
            total = mono(f"{diffs.sum():.2f}", size=26, color=GOLD)
            total.move_to(np.array([x_diff, TOP_Y - 10.2 * ROW_DY, 0]))
            self.play(Create(rule), run_time=0.4)
            self.play(
                TransformFromCopy(diff_col, total),
                run_time=1.2,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Untrained, mine started at two point seven. The whole job now is making that "
            "number smaller."
        ) as t:
            label = mono("loss", size=30, color=GOLD).next_to(total, LEFT, buff=0.4)
            self.play(FadeIn(label, shift=RIGHT * 0.2), Flash(total, color=GOLD, line_length=0.2), run_time=0.9)
            self.play(
                FadeIn(place_chips(chips("target: [0,0,0,0,0,1,0,0,0,0]", f"loss = {loss_val:.2f}"))),
                run_time=0.6,
            )
            arrow = Arrow(
                total.get_bottom() + DOWN * 0.15,
                total.get_bottom() + DOWN * 0.95,
                color=GREEN, stroke_width=5, buff=0,
            )
            smaller = mono("smaller", size=22, color=GREEN).next_to(arrow, DOWN, buff=0.12)
            self.play(GrowArrow(arrow), FadeIn(smaller), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
