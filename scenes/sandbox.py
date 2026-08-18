"""Interaktiv lekegrind — vår versjon av 3b1b sitt IPython-vindu.

    make play

Åpner et OpenGL-vindu med en levende scene, og et IPython-skall i terminalen
som skriver rett inn i det vinduet. Alt fra scenes.common er importert, så du
kan prøve ting med én gang:

    self.add(digit_image(run()["x_test"][0]))
    self.play(FadeIn(body("hei")))
    self.clear()

I skallet:
    self.play / self.add / self.remove / self.wait   virker på vinduet direkte
    rerun                                            kjører construct() på nytt
    %paste                                           limer inn kode fra utklippstavla
    exit                                             lukker skallet, scenen avsluttes

I vinduet kan du dra med musa for å panorere og scrolle for å zoome.

Lagrer du denne fila mens vinduet står åpent, kjøres scenen automatisk på nytt.
NB: endringer i scenes/common.py plukkes ikke opp av den auto-rerunen — den
laster bare denne fila på nytt. Start på nytt hvis du har endret felleskoden.
"""

from manim import *  # noqa: F403

import scenes.common as c


class Sandbox(Scene):
    def construct(self):
        # interactive_embed() bygger navnerommet sitt av de lokale variablene i
        # construct(), ikke av modulens import. Derfor drar vi felleskoden inn
        # hit — da kan du skrive body(...) og run() rett i skallet. Resten av
        # scenes/common.py ligger uansett på `c.`.
        BG, FG, MUTED, DIM = c.BG, c.FG, c.MUTED, c.DIM
        ACCENT, WARM, GOLD, GREEN, VIOLET = c.ACCENT, c.WARM, c.GOLD, c.GREEN, c.VIOLET
        body, mono, formula = c.body, c.mono, c.formula
        chip, chips, place_chips, backdrop = c.chip, c.chips, c.place_chips, c.backdrop
        digit_image, pixel_grid, neuron, axis_ticks = (
            c.digit_image, c.pixel_grid, c.neuron, c.axis_ticks
        )
        weight_sheet, signed_rgb, image_from_array = (
            c.weight_sheet, c.signed_rgb, c.image_from_array
        )
        run = c.run

        self.add(c.mono("sandbox", size=20, color=c.MUTED).to_corner(UL))
        self.interactive_embed()
