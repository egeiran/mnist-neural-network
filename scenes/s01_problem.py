"""Scene 1 — The problem (0:00–0:45)."""

from manim import *

from scenes.common import (
    ACCENT,
    GOLD,
    MUTED,
    NarratedScene,
    body,
    chips,
    digit_image,
    place_chips,
    run,
)


class S01Problem(NarratedScene):
    def construct(self):
        data = run()
        images = data["showcase_images"]
        acc = float(data["epoch_acc"][-1]) * 100

        five = digit_image(images[0], height=4.4)

        with self.narrate(
            "This is a five. You knew that instantly, and you have no idea how you knew it."
        ) as t:
            self.play(FadeIn(five, scale=1.06), run_time=min(2.2, t.duration * 0.4))
            self.wait(min(1.0, t.duration * 0.2))

        # De fire rotete — 4 som ligner 9, 7 med strek, 3 som ligner 5, 9 som ligner 4
        offsets = [
            LEFT * 4.6 + UP * 1.9,
            RIGHT * 4.6 + UP * 1.9,
            LEFT * 4.6 + DOWN * 1.9,
            RIGHT * 4.6 + DOWN * 1.9,
        ]
        messy = Group(
            *[digit_image(v, height=2.3).move_to(o) for v, o in zip(images[1:], offsets)]
        )

        with self.narrate(
            "There is no rule you could write down. No list of \"if the top is flat and "
            "there's a loop at the bottom.\" People have tried, and it does not work, "
            "because every person writes a five slightly differently."
        ) as t:
            self.play(
                LaggedStart(
                    *[FadeIn(m, shift=UP * 0.25) for m in messy],
                    lag_ratio=0.35,
                ),
                run_time=min(3.2, t.duration * 0.45),
            )
            rules = VGroup(
                body("if top_is_flat and has_loop_below:", 26, MUTED),
                body("    return 5", 26, MUTED),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            rules.to_edge(DOWN, buff=0.5)
            self.play(FadeIn(rules), run_time=0.6)
            self.wait(min(1.2, max(t.get_remaining_duration() - 1.4, 0.2)))
            cross = Line(
                rules.get_left() + LEFT * 0.15,
                rules.get_right() + RIGHT * 0.15,
                color="#ff7b72",
                stroke_width=5,
            )
            self.play(Create(cross), run_time=0.5)
            self.play(FadeOut(rules, cross), run_time=0.5)

        # Alle fem krymper ned i en rad
        all_five = Group(five, *messy)
        row = Group(*[m.copy().set(height=1.7) for m in all_five])
        row.arrange(RIGHT, buff=0.45)
        row.move_to(UP * 0.6)

        with self.narrate(
            "So instead of writing the rules, I built something that finds the rules on its own. "
            "About four hundred lines of Python, no machine learning libraries, just NumPy for "
            "the matrix math. It gets ninety-seven and a half percent of handwritten digits right."
        ) as t:
            self.play(
                *[
                    m.animate.scale(target.height / m.height).move_to(target.get_center())
                    for m, target in zip(all_five, row)
                ],
                run_time=2.0,
            )

            tags = place_chips(chips("no libraries.  just NumPy.", f"{acc:.2f}% accuracy"))
            tags[1][1].set_color(GOLD)
            self.play(
                LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in tags], lag_ratio=0.4),
                run_time=1.2,
            )

        with self.narrate("Here's how it works.") as t:
            line = Line(LEFT * 2, RIGHT * 2, color=ACCENT, stroke_width=3)
            line.next_to(row, DOWN, buff=1.0)
            self.play(GrowFromCenter(line), run_time=0.8)

        self.clear_out()
