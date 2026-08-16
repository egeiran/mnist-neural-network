"""Manim-animasjoner for MNIST-nettverket.

Kjør med prosjektets venv:
    .venv/bin/manim -pql animasjon.py Arkitektur
    .venv/bin/manim -pql animasjon.py SifferTilVektor
"""

import numpy as np
from manim import *

from data import load_data


class Arkitektur(Scene):
    """Tegner feedforward-arkitekturen 784 -> 16 -> 10."""

    def construct(self):
        input_lag = self.lag(8, BLUE, avkortet=True)
        skjult_lag = self.lag(6, TEAL)
        output_lag = self.lag(10, YELLOW)

        lagene = VGroup(input_lag, skjult_lag, output_lag).arrange(RIGHT, buff=2.2)
        lagene.scale_to_fit_height(5.5).move_to(ORIGIN)

        etiketter = VGroup(
            Text("784", font_size=28).next_to(input_lag, DOWN, buff=0.4),
            Text("16", font_size=28).next_to(skjult_lag, DOWN, buff=0.4),
            Text("10", font_size=28).next_to(output_lag, DOWN, buff=0.4),
        )

        kanter = VGroup()
        for venstre, hoyre in ((input_lag, skjult_lag), (skjult_lag, output_lag)):
            for a in venstre:
                for b in hoyre:
                    kanter.add(Line(a.get_right(), b.get_left(), stroke_width=1, stroke_opacity=0.25))

        self.play(LaggedStart(*[GrowFromCenter(n) for n in lagene.family_members_with_points()
                                if isinstance(n, Circle)], lag_ratio=0.02))
        self.play(Create(kanter), run_time=1.5)
        self.play(Write(etiketter))

        # La en aktivering "renne" gjennom nettverket.
        for lag in (input_lag, skjult_lag, output_lag):
            self.play(LaggedStart(*[n.animate.set_fill(opacity=0.9) for n in lag],
                                  lag_ratio=0.05), run_time=0.8)
        self.wait()

    def lag(self, antall, farge, avkortet=False):
        noder = VGroup(*[Circle(radius=0.22, color=farge, stroke_width=2).set_fill(farge, opacity=0.0)
                         for _ in range(antall)])
        noder.arrange(DOWN, buff=0.25)
        if avkortet:
            # Marker at input-laget egentlig har 784 noder.
            prikker = VGroup(*[Dot(radius=0.03, color=farge) for _ in range(3)]).arrange(DOWN, buff=0.12)
            noder.insert(antall // 2, prikker)
            noder.arrange(DOWN, buff=0.25)
        return noder


class SifferTilVektor(Scene):
    """Viser et ekte MNIST-siffer og bretter det ut til en 784-vektor."""

    def construct(self):
        X_train, _, y_train, _ = load_data()
        bilde_data = X_train[0].reshape(28, 28)
        fasit = int(np.argmax(y_train[0]))  # y_train er one-hot fra data.py

        bilde = ImageMobject((bilde_data * 255).astype(np.uint8))
        bilde.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        bilde.height = 4
        bilde.to_edge(LEFT, buff=1.5)

        tittel = Text(f"MNIST-siffer: {fasit}", font_size=32).next_to(bilde, UP, buff=0.4)

        self.play(FadeIn(bilde), Write(tittel))
        self.wait(0.5)

        # Bygg en kolonne som antyder inputvektoren (et utvalg av de 784 verdiene).
        utvalg = bilde_data.flatten()[::56][:14]
        celler = VGroup(*[
            Square(side_length=0.32, stroke_width=1, stroke_color=GREY)
            .set_fill(WHITE, opacity=float(v))
            for v in utvalg
        ]).arrange(DOWN, buff=0.02)
        celler.add(Text("...", font_size=24).rotate(PI / 2))
        celler.arrange(DOWN, buff=0.05).move_to(RIGHT * 2)

        ramme = SurroundingRectangle(celler, color=BLUE, buff=0.15)
        vektor_tekst = Text("x  (784 x 1)", font_size=26).next_to(ramme, UP, buff=0.3)

        # ImageMobject er ikke en VMobject, så den kan ikke Transform-es til en VGroup.
        pil = Arrow(bilde.get_right(), celler.get_left(), buff=0.4, color=GREY_B)
        self.play(GrowArrow(pil))
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in celler], lag_ratio=0.08),
                  run_time=2)
        self.play(Create(ramme), Write(vektor_tekst))
        self.wait(2)
