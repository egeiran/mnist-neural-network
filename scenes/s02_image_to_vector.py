"""Scene 2 — From image to numbers (0:45–1:25).

Manusets visuelle hook: 28×28-rutenettet rulles ut, rad for rad, til én
784 lang kolonne.
"""

import numpy as np
from manim import *

from scenes.common import (
    ACCENT,
    DIM,
    GOLD,
    MUTED,
    NarratedScene,
    backdrop,
    body,
    chips,
    digit_image,
    mono,
    node_column,
    pixel_grid,
    place_chips,
    run,
)

CELL = 0.2


def best_patch(img: np.ndarray, size: int = 6) -> tuple[int, int]:
    """Finn en 6x6-flekk med både mørke og lyse piksler."""
    best, best_score = (0, 0), -1.0
    for r in range(4, 24 - size):
        for c in range(4, 24 - size):
            patch = img[r : r + size, c : c + size]
            score = float(patch.std()) + 0.4 * float((patch < 0.05).mean())
            if score > best_score:
                best, best_score = (r, c), score
    return best


class S02ImageToVector(NarratedScene):
    def construct(self):
        data = run()
        vec = data["showcase_images"][0]
        img28 = vec.reshape(28, 28)

        picture = digit_image(vec, height=28 * CELL)
        grid = pixel_grid(vec, cell=CELL)

        with self.narrate(
            "A computer doesn't see a five. It sees a grid — twenty-eight by twenty-eight, "
            "seven hundred and eighty-four little squares, each holding a brightness value "
            "from zero to two fifty-five."
        ) as t:
            self.play(FadeIn(picture), run_time=0.8)
            self.wait(0.5)
            # Rutenettet legger seg over bildet
            self.play(FadeIn(grid), FadeOut(picture), run_time=1.4)

            tags = backdrop(place_chips(chips("28 × 28 = 784 pixels")))
            self.play(FadeIn(tags), run_time=0.5)

            # Zoom inn på en flekk og vis de faktiske tallene
            r0, c0 = best_patch(img28)
            idx = [(r0 + dr) * 28 + (c0 + dc) for dr in range(6) for dc in range(6)]
            patch = VGroup(*[grid[i] for i in idx])
            center = patch.get_center()

            grid.save_state()
            k = 3.6
            self.play(
                grid.animate.scale(k, about_point=center).shift(-center + LEFT * 1.2),
                run_time=1.6,
            )

            numbers = VGroup()
            for i in idx:
                raw = int(round(float(img28[i // 28, i % 28]) * 255))
                col = GOLD if raw > 0 else MUTED
                numbers.add(mono(str(raw), size=17, color=col).move_to(grid[i].get_center()))
            self.play(
                LaggedStart(*[FadeIn(n, scale=0.7) for n in numbers], lag_ratio=0.02),
                run_time=1.4,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "First thing I do is divide everything by two fifty-five, so every pixel sits "
            "between zero and one. That matters more than it sounds like, and I'll come back to why."
        ) as t:
            div = backdrop(mono("÷ 255", size=40, color=ACCENT).to_corner(UR, buff=0.7))
            self.play(FadeIn(div, shift=LEFT * 0.3), run_time=0.7)

            scaled = VGroup()
            for n, i in zip(numbers, idx):
                val = float(img28[i // 28, i % 28])
                col = GOLD if val > 0 else MUTED
                scaled.add(mono(f"{val:.2f}", size=16, color=col).move_to(n.get_center()))
            self.play(
                LaggedStart(
                    *[Transform(a, b) for a, b in zip(numbers, scaled)],
                    lag_ratio=0.02,
                ),
                run_time=1.6,
            )

            self.play(
                FadeIn(backdrop(place_chips(chips("pixel ÷ 255 → [0, 1]")).shift(UP * 0.62))),
                run_time=0.5,
            )
            self.wait(max(t.get_remaining_duration() - 1.1, 0.1))
            self.play(FadeOut(numbers), FadeOut(div), run_time=0.6)

        # --- Utrullingen ------------------------------------------------------
        with self.narrate(
            "Then I unroll the grid. Row by row, into one long column of seven hundred "
            "and eighty-four numbers. The image is now just a list. That's the input."
        ) as t:
            self.play(
                Restore(grid),
                run_time=1.0,
            )
            self.play(grid.animate.scale(0.78).move_to(LEFT * 3.7), run_time=0.8)

            flat = vec.reshape(-1)
            col = node_column(flat, radius=0.13, buff=0.17, labels=True, label_size=16)
            col.move_to(np.array([1.9, 0, 0]))
            col_x = col.nodes.get_center()[0]

            frame = SurroundingRectangle(col, color=DIM, stroke_width=2, buff=0.28)
            self.play(Create(frame), run_time=0.6)

            # Hver rad i rutenettet flyr bort til den høyden tallene sine ville
            # hatt i kolonnen, og krymper vekk der. Nodene dukker opp i samme
            # rekkefølge, så lista ser ut til å fylles ovenfra og ned.
            unroll = 4.0
            rows = [VGroup(*grid[r * 28 : (r + 1) * 28]) for r in range(28)]
            fly = [
                row.animate.stretch_to_fit_height(0.03)
                .stretch_to_fit_width(0.5)
                .move_to(np.array([col_x, col.y_of(r * 28 + 14), 0]))
                .set_opacity(0)
                for r, row in enumerate(rows)
            ]

            def when(i: float) -> float:
                return float(np.clip(i / 783 * unroll - 0.25, 0.01, unroll - 0.4))

            popping = [
                Succession(Wait(when(i)), FadeIn(entry, scale=0.6, run_time=0.4))
                for entry, i in zip(col.entries, col.indices)
            ] + [
                Succession(Wait(when(i)), FadeIn(d, run_time=0.4))
                for d, i in zip(col.dots, col.dot_indices)
            ]

            self.play(
                LaggedStart(*fly, lag_ratio=0.085, run_time=unroll),
                AnimationGroup(*popping),
            )
            self.remove(*rows, grid)

            brace = Brace(frame, RIGHT, color=MUTED)
            label = mono("784", size=34, color=GOLD).next_to(brace, RIGHT, buff=0.2)
            caption = body("one long list of numbers", 26, MUTED)
            caption.next_to(frame, DOWN, buff=0.4)
            self.play(GrowFromCenter(brace), FadeIn(label), FadeIn(caption), run_time=0.9)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.2))

        self.clear_out()
