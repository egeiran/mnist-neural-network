"""Scene 5 — Layers and matrices (3:15–3:55).

Scenen bygger matrisen i stedet for å påstå den: én nevrons vifte av ledninger
kollapser til én kolonne med vekter, de to første kolonnene krymper til den
bredden en kolonne faktisk har når 128 skal få plass, og resten fylles inn til
W1 står der. Deretter kjøres selve matriseproduktet som en mekanisme — rad
ganger kolonne blir én celle — i det klassiske L-oppsettet der X ligger til
venstre for Z og W rett over, slik at innerdimensjonene møtes.

Alle tallene er ekte: W1 er vektene før trening (biasene starter på null, så
Z = X @ W1 stemmer på desimalen), og X er den samme utrente batchen på 32 bilder
som scene 8 regner gradienter på.
"""

import numpy as np
from manim import *

from scenes.common import (
    ACCENT,
    BG,
    DIM,
    FG,
    GOLD,
    GREEN,
    MUTED,
    NarratedScene,
    VIOLET,
    WARM,
    body,
    chips,
    image_from_array,
    mono,
    neuron,
    node_column,
    place_chips,
    run,
    signed_rgb,
    weight_scale,
)

BG_RGB = (np.array(ManimColor(BG).to_rgb()) * 255).astype(np.uint8)


def edge(n: int) -> float:
    """Kantlengde for en dimensjon, i sceneenheter.

    Kvadratrot og ikke lineært — lineært ville gjort 784 fire meter bred og 10
    usynlig. Det som betyr noe er at samme tall gir samme kantlengde overalt,
    slik at innerdimensjonene i X @ W faktisk er like lange og kan møtes."""
    return 0.42 + 0.095 * float(np.sqrt(n))


def gray_rgb(M: np.ndarray) -> np.ndarray:
    """(h, w) i 0–1 → gråtoner som RGB."""
    g = (np.clip(M, 0, 1) * 255).astype(np.uint8)
    return np.repeat(g[..., None], 3, axis=2)


def sheet(rgb: np.ndarray, width: float, height: float) -> ImageMobject:
    img = image_from_array(rgb.copy(), height=height)
    img.stretch_to_fit_width(width)
    return img


def framed(img: Mobject, color: str = DIM, width: float = 2) -> Rectangle:
    return SurroundingRectangle(img, color=color, stroke_width=width, buff=0.0)


def reveal(full: np.ndarray, tracker: ValueTracker):
    """Fyller et bilde kolonne for kolonne — brukes både til å bygge W og til å
    la sveipet over W etterlate seg ferdig utregnede kolonner i Z."""

    def update(mob):
        k = int(np.clip(round(tracker.get_value()), 0, full.shape[1]))
        mob.pixel_array[:, :k, :3] = full[:, :k]
        mob.pixel_array[:, k:, :3] = BG_RGB

    return update


class S05LayersMatrices(NarratedScene):
    def construct(self):
        data = run()
        W1 = np.asarray(data["W1_init"], dtype=np.float32)
        demo = np.asarray(data["demo_image"], dtype=np.float32)
        batch = np.asarray(data["batch_images"], dtype=np.float32)
        hidden0 = np.asarray(data["untrained_hidden"], dtype=np.float32)
        out0 = np.asarray(data["untrained_out"], dtype=np.float32)

        w_scale = weight_scale(W1)
        W_RGB = signed_rgb(W1, scale=w_scale)
        Z1 = demo[None, :] @ W1          # b starter på null → dette *er* Z
        Z32 = batch @ W1
        z_scale = weight_scale(Z32)
        Z1_RGB = signed_rgb(Z1, scale=z_scale)
        Z32_RGB = signed_rgb(Z32, scale=z_scale)

        # =====================================================================
        # 1 — ett nevron blir til hundre og tjueåtte
        # =====================================================================
        col_h = 4.4
        x_in, x_cells = -5.2, -1.9

        nodes = node_column(demo, radius=0.1, buff=0.13, height=col_h)
        nodes.move_to([x_in, 0.15, 0])
        col_frame = SurroundingRectangle(nodes, color=DIM, stroke_width=2, buff=0.2)
        col_tag = mono("784 pixels", size=20, color=MUTED).next_to(col_frame, DOWN, buff=0.2)
        column = VGroup(nodes, col_frame, col_tag)

        one = neuron(radius=0.3, value=0.62).move_to([x_cells, 0.15, 0])

        def fan(target, every=1, width=1.0, opacity=0.5):
            """Ledninger fra nodene vi viser og bort til ett nevron."""
            return VGroup(
                *[
                    Line(
                        node.get_right() + RIGHT * 0.02,
                        target.get_left(),
                        stroke_width=width,
                        stroke_color=ACCENT,
                        stroke_opacity=opacity,
                    )
                    for node in nodes.nodes[::every]
                ]
            )

        with self.narrate(
            "One neuron asks one question. A layer is a hundred and twenty-eight neurons asking "
            "a hundred and twenty-eight different questions at the same time."
        ) as t:
            self.play(FadeIn(column), run_time=1.0)
            self.play(GrowFromCenter(one), run_time=0.6)
            wires = fan(one)
            caption = body("one question", 24, MUTED).move_to([x_cells, -2.35, 0])
            self.play(Create(wires), FadeIn(caption), run_time=1.3)

            cells = node_column(
                hidden0, n_top=5, n_mid=4, n_bottom=4,
                radius=0.12, buff=0.15, color=ACCENT, height=3.5,
            )
            cells.move_to([x_cells, 0.15, 0])
            brace = Brace(cells, RIGHT, color=MUTED)
            brace_tag = mono("128 neurons", size=22, color=MUTED).next_to(brace, RIGHT, buff=0.18)

            fans = [fan(c, every=2, width=0.5, opacity=0.35) for c in cells.nodes]
            all_wires = VGroup(*fans)
            caption2 = body("128 questions at once", 24, MUTED).move_to(caption)

            self.play(
                ReplacementTransform(one, cells),
                ReplacementTransform(wires, all_wires),
                ReplacementTransform(caption, caption2),
                run_time=1.9,
            )
            self.play(GrowFromCenter(brace), FadeIn(brace_tag), run_time=0.7)
            # tre av dem, én om gangen — de spør ikke om det samme
            self.play(
                LaggedStart(
                    *[
                        Indicate(cells.nodes[i], color=GOLD, scale_factor=1.5)
                        for i in (1, 6, 10)
                    ],
                    lag_ratio=0.45,
                ),
                run_time=1.6,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # =====================================================================
        # 2 — ett nevron er én kolonne; 128 kolonner er matrisen
        # =====================================================================
        W_W, W_H = 2.7, col_h
        x_mat = 0.2                        # venstrekanten til både slivere og matrise
        y_mat = 0.15
        cw = W_W / 128                     # bredden på én kolonne i den ferdige matrisa
        strip_w, strip_gap = 0.55, 0.12

        with self.narrate(
            "Each one has its own seven hundred and eighty-four weights, so I stack them into "
            "a grid — a matrix. Seven eighty-four by one twenty-eight. Right now they're random "
            "numbers — what they become is the last thing I'll show you."
        ) as t:
            self.play(FadeOut(brace), FadeOut(brace_tag), FadeOut(caption2), run_time=0.4)

            strips, done = [], set()
            for k in (0, 1):
                # bare ledninger som fortsatt er på skjermen dempes — ellers
                # ville .animate dratt de allerede fjernede inn igjen
                rest_w = VGroup(*[f for i, f in enumerate(fans) if i != k and i not in done])
                rest_c = VGroup(*[c for i, c in enumerate(cells.nodes) if i != k])
                self.play(
                    rest_w.animate.set_stroke(opacity=0.05),
                    rest_c.animate.set_opacity(0.2),
                    fans[k].animate.set_stroke(color=GOLD, width=1.1, opacity=0.9),
                    cells.nodes[k].animate.set_stroke(color=GOLD, width=2.5),
                    run_time=0.55,
                )
                s = sheet(signed_rgb(W1[:, k : k + 1], scale=w_scale), strip_w, col_h)
                s.move_to([x_mat + strip_w / 2 + k * (strip_w + strip_gap), y_mat, 0])
                strips.append(s)
                self.play(
                    FadeOut(fans[k], shift=RIGHT * 0.7),
                    FadeIn(s, shift=RIGHT * 0.7),
                    run_time=1.0,
                )
                done.add(k)
                if k == 0:
                    note = body("one neuron  →  one column of 784 weights", 22, MUTED)
                    note.next_to(strips[0], DOWN, buff=0.35).align_to(strips[0], LEFT)
                    self.play(FadeIn(note), run_time=0.4)

            # ... og så de 126 andre. Sliverne krymper til den bredden en kolonne
            # faktisk har når alle 128 skal stå ved siden av hverandre.
            W_img = sheet(W_RGB, W_W, W_H)
            W_img.move_to([x_mat + W_W / 2, y_mat, 0])
            fill = ValueTracker(0)
            painter = reveal(W_RGB, fill)
            W_img.add_updater(painter)
            self.add(W_img)

            self.play(
                strips[0].animate.stretch_to_fit_width(cw).move_to([x_mat + 0.5 * cw, y_mat, 0]),
                strips[1].animate.stretch_to_fit_width(cw).move_to([x_mat + 1.5 * cw, y_mat, 0]),
                FadeOut(all_wires), FadeOut(cells), FadeOut(note),
                run_time=0.9,
            )
            self.play(
                fill.animate.set_value(128),
                run_time=3.4,
                rate_func=rate_functions.ease_out_cubic,
            )
            W_img.remove_updater(painter)
            self.remove(*strips)

            w_frame = framed(W_img)
            b_left = Brace(w_frame, LEFT, color=MUTED)
            b_top = Brace(w_frame, UP, color=MUTED)
            t_left = mono("784", size=21, color=MUTED).next_to(b_left, LEFT, buff=0.14)
            t_top = mono("128", size=21, color=MUTED).next_to(b_top, UP, buff=0.14)
            # tittel og undertittel holdes fra hverandre: undertittelen byttes ut
            # under, og en VGroup i scenen ville dratt den gamle inn igjen
            w_title = mono("W1", size=26, color=FG)
            w_sub = mono("one column per neuron", size=19, color=MUTED)
            VGroup(w_title, w_sub).arrange(DOWN, buff=0.12).next_to(w_frame, DOWN, buff=0.3)

            self.play(
                Create(w_frame),
                GrowFromCenter(b_left), GrowFromCenter(b_top),
                FadeIn(t_left), FadeIn(t_top), FadeIn(w_title), FadeIn(w_sub),
                run_time=1.0,
            )
            legend = VGroup(
                mono("blue = positive weight", size=18, color=ACCENT),
                mono("red  = negative weight", size=18, color=WARM),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).to_corner(UR, buff=0.5)
            self.play(FadeIn(legend), run_time=0.4)

            # Et lite utsnitt forstørret opp: bildet *er* tall. Verdiene er de
            # ekte cellene i W1_init, og fortegnet gir fargen — samme kode som
            # matrisen selv bruker.
            r0, c0, nr, nc = 40, 3, 4, 3
            patch = W1[r0 : r0 + nr, c0 : c0 + nc]
            cell_w, cell_h = W_W / 128, W_H / 784
            zoom = Rectangle(
                width=max(nc * cell_w, 0.16), height=max(nr * cell_h, 0.16),
                stroke_color=GOLD, stroke_width=2,
            ).move_to([
                x_mat + (c0 + nc / 2) * cell_w,
                y_mat + W_H / 2 - (r0 + nr / 2) * cell_h,
                0,
            ])
            grid = VGroup(
                *[
                    mono(f"{v:+.3f}", size=15, color=ACCENT if v > 0 else WARM)
                    for row in patch
                    for v in row
                ]
            ).arrange_in_grid(nr, nc, buff=0.22)
            box = SurroundingRectangle(grid, color=DIM, stroke_width=2, buff=0.26)
            callout = VGroup(grid, box).move_to([4.8, 0.15, 0])
            links = VGroup(
                *[
                    Line(zoom.get_corner(c), box.get_corner(d),
                         stroke_color=GOLD, stroke_width=1, stroke_opacity=0.45)
                    for c, d in ((UR, UL), (DR, DL))
                ]
            )
            self.play(Create(zoom), Create(links), run_time=0.7)
            self.play(Create(box), FadeIn(grid, lag_ratio=0.08), run_time=1.4)

            # 784 × 128 er nøyaktig like mange tall som det blir gange-og-legg-
            # sammen per bilde i neste beat
            w_sub2 = mono("100,352 random numbers — for now", size=19, color=GOLD)
            w_sub2.move_to(w_sub)
            self.play(
                FadeOut(w_sub, shift=UP * 0.12),
                FadeIn(w_sub2, shift=UP * 0.12),
                run_time=0.8,
            )
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # =====================================================================
        # 3 — Z = X @ W + b, som mekanisme
        # =====================================================================
        E784, E128, E32 = edge(784), edge(128), edge(32)
        E1 = 0.34                                  # ett bilde, tegnet så det synes
        colw = E128 / 128                          # én kolonne i W, i sceneenheter
        band_w = max(colw, 0.05)

        w_cx, w_cy = 2.35, 1.22                    # W: 784 høy, 128 bred
        row_cy = -1.45                             # X og Z ligger på samme høyde
        x_cx = w_cx - E128 / 2 - 0.55 - E784 / 2   # X rett til venstre for Z
        panel = np.array([-4.55, 0.0, 0.0])        # tomt felt til venstre

        def col_x(j):
            return w_cx - E128 / 2 + (j + 0.5) * colw

        with self.narrate(
            "And now the whole layer is one line of code. Inputs times weights, plus bias. "
            "That's not new math, it's just bookkeeping. The matrix multiply does a hundred "
            "thousand multiply-and-adds in a single operation, and it does it for thirty-two "
            "images at once."
        ) as t:
            # W flytter inn i oppsettet — det er den samme matrisa vi nettopp bygde
            self.play(
                FadeOut(column), FadeOut(legend), FadeOut(w_title), FadeOut(w_sub2),
                FadeOut(zoom), FadeOut(links), FadeOut(callout),
                FadeOut(b_left), FadeOut(b_top), FadeOut(t_left), FadeOut(t_top),
                W_img.animate.stretch_to_fit_width(E128).stretch_to_fit_height(E784)
                     .move_to([w_cx, w_cy, 0]),
                w_frame.animate.stretch_to_fit_width(E128).stretch_to_fit_height(E784)
                       .move_to([w_cx, w_cy, 0]),
                run_time=1.1,
            )
            w_lab = VGroup(
                mono("W", size=24, color=ACCENT),
                mono("784 × 128", size=18, color=MUTED),
            ).arrange(DOWN, buff=0.1).next_to(w_frame, UP, buff=0.18)

            X_img = sheet(gray_rgb(demo[None, :]), E784, E1).move_to([x_cx, row_cy, 0])
            x_frame = framed(X_img, color=GOLD)
            x_lab = mono("X   1 × 784", size=18, color=GOLD).next_to(x_frame, DOWN, buff=0.16)
            thumb = image_from_array(gray_rgb(demo.reshape(28, 28)), height=0.44)
            thumb.next_to(x_frame, LEFT, buff=0.22)

            jt = ValueTracker(0)
            Z_img = sheet(Z1_RGB, E128, E1).move_to([w_cx, row_cy, 0])
            zpaint = reveal(Z1_RGB, jt)
            Z_img.add_updater(zpaint)
            z_frame = framed(Z_img, color=GREEN)
            z_lab = mono("Z   1 × 128", size=18, color=GREEN).next_to(z_frame, DOWN, buff=0.16)

            b_bar = Rectangle(
                width=E128, height=0.16, stroke_color=VIOLET, stroke_width=2,
                fill_color=VIOLET, fill_opacity=0.35,
            ).move_to([w_cx, row_cy - E32 / 2 - 0.75, 0])
            b_lab = mono("b   128", size=18, color=VIOLET).next_to(b_bar, DOWN, buff=0.14)

            self.play(
                FadeIn(w_lab), FadeIn(thumb), FadeIn(X_img),
                Create(x_frame), FadeIn(x_lab),
                run_time=0.9,
            )
            self.add(Z_img)                       # står tomt til det er regnet ut
            self.play(Create(z_frame), FadeIn(z_lab), FadeIn(b_bar), FadeIn(b_lab), run_time=0.6)

            # --- formene: innerdimensjonene møtes og stryker hverandre -------
            p32 = mono("32", size=28, color=GOLD)
            x1 = mono("×", size=24, color=MUTED)
            p784a = mono("784", size=28, color=FG)
            at = mono("@", size=28, color=MUTED)
            p784b = mono("784", size=28, color=FG)
            x2 = mono("×", size=24, color=MUTED)
            p128 = mono("128", size=28, color=GREEN)
            shape = VGroup(p32, x1, p784a, at, p784b, x2, p128)
            shape.arrange(RIGHT, buff=0.2).move_to(panel + UP * 2.35)
            self.play(FadeIn(shape), run_time=0.5)
            self.play(p784a.animate.set_color(GOLD), p784b.animate.set_color(GOLD), run_time=0.35)

            res = VGroup(
                mono("32", size=28, color=GOLD),
                mono("×", size=24, color=MUTED),
                mono("128", size=28, color=GREEN),
            ).arrange(RIGHT, buff=0.2).move_to(shape)
            mid = shape.get_center()
            self.play(
                FadeOut(p784a, target_position=mid, scale=0.2),
                FadeOut(p784b, target_position=mid, scale=0.2),
                FadeOut(at, scale=0.2), FadeOut(x1, scale=0.2), FadeOut(x2, scale=0.2),
                ReplacementTransform(p32, res[0]),
                FadeIn(res[1]),
                ReplacementTransform(p128, res[2]),
                run_time=0.9,
            )
            shape_note = mono("the inner 784s must match", size=18, color=MUTED)
            shape_note.next_to(res, DOWN, buff=0.24)
            self.play(FadeIn(shape_note), run_time=0.4)

            # --- én celle: én rad ganger én kolonne --------------------------
            band = always_redraw(
                lambda: Rectangle(
                    width=band_w, height=E784, stroke_color=GOLD,
                    stroke_width=2.5, fill_opacity=0,
                ).move_to([col_x(min(jt.get_value(), 127)), w_cy, 0])
            )
            row = Rectangle(width=E784, height=E1, stroke_color=GOLD, stroke_width=2.5,
                            fill_opacity=0).move_to(X_img)
            col0 = Rectangle(width=band_w, height=E784, stroke_color=GOLD, stroke_width=2.5,
                             fill_opacity=0).move_to([col_x(0), w_cy, 0])
            cell = Rectangle(width=band_w, height=E1, stroke_color=GOLD, stroke_width=2.5,
                             fill_opacity=0).move_to([col_x(0), row_cy, 0])

            self.play(Create(row), FadeIn(band), run_time=0.5)
            self.play(Transform(row, cell), Transform(col0, cell), run_time=0.8)
            self.remove(row, col0)
            self.play(
                jt.animate.set_value(1),
                Flash(cell.get_center(), color=GOLD, line_length=0.12, flash_radius=0.3),
                FadeIn(cell),
                run_time=0.6,
            )
            calc = VGroup(
                mono("one cell of Z", size=19, color=MUTED),
                mono("784 multiplies + 783 adds", size=19, color=MUTED),
            ).arrange(DOWN, buff=0.14).move_to(panel + UP * 0.85)
            self.play(FadeIn(calc), run_time=0.4)

            # --- sveip: hele Z fylles, telleren ruller ------------------------
            counter = always_redraw(
                lambda: mono(
                    f"{int(round(jt.get_value())) * 784:,}  multiply-and-adds",
                    size=23, color=GOLD,
                ).move_to(panel + DOWN * 0.15)
            )
            self.add(counter)
            self.play(FadeOut(cell), run_time=0.25)
            self.play(jt.animate.set_value(128), run_time=3.2, rate_func=linear)
            self.remove(band)
            Z_img.remove_updater(zpaint)

            # --- pluss bias: den samme raden legges på hver rad ---------------
            ghosts = [b_bar.copy() for _ in range(3)]
            self.play(
                LaggedStart(
                    *[g.animate.move_to(Z_img.get_center()).set_opacity(0) for g in ghosts],
                    lag_ratio=0.25,
                ),
                Indicate(z_frame, color=VIOLET, scale_factor=1.03),
                run_time=1.0,
            )
            self.remove(*ghosts)

            # --- 32 bilder om gangen -----------------------------------------
            X32 = sheet(gray_rgb(batch), E784, E1).move_to(X_img)
            Z32_img = sheet(Z32_RGB, E128, E1).move_to(Z_img)
            self.add(X32, Z32_img)
            self.remove(X_img, Z_img)
            x_lab2 = mono("X   32 × 784", size=18, color=GOLD)
            z_lab2 = mono("Z   32 × 128", size=18, color=GREEN)
            x_lab2.move_to([x_cx, row_cy - E32 / 2 - 0.28, 0])
            z_lab2.move_to([w_cx, row_cy - E32 / 2 - 0.28, 0])
            self.play(
                X32.animate.stretch_to_fit_height(E32),
                Z32_img.animate.stretch_to_fit_height(E32),
                x_frame.animate.stretch_to_fit_height(E32),
                z_frame.animate.stretch_to_fit_height(E32),
                ReplacementTransform(x_lab, x_lab2),
                ReplacementTransform(z_lab, z_lab2),
                run_time=1.1,
            )
            self.remove(counter)
            total = VGroup(
                mono("100,352  per image", size=22, color=MUTED),
                mono("× 32 images  =  3,211,264", size=23, color=GOLD),
            ).arrange(DOWN, buff=0.16).move_to(panel + DOWN * 0.2)
            self.play(FadeIn(total), run_time=0.5)

            code = mono("Z = X @ W + b", size=32, color=FG).move_to([-5.0, -1.55, 0])
            self.play(FadeIn(code, shift=UP * 0.15), run_time=0.6)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # =====================================================================
        # 4 — andre lag: trakta 784 → 128 → 10
        # =====================================================================
        with self.narrate(
            "Then a second layer takes those hundred and twenty-eight answers down to ten. "
            "One output per digit."
        ) as t:
            self.play(
                FadeOut(Group(X32, Z32_img, thumb, W_img)),
                FadeOut(VGroup(x_frame, z_frame, w_frame, w_lab, b_bar, b_lab,
                               x_lab2, z_lab2, res, shape_note, calc, total, code)),
                run_time=0.7,
            )

            v784 = sheet(gray_rgb(demo[None, :]), edge(784), 0.44)
            v128 = sheet(Z1_RGB, edge(128), 0.44)
            v10 = sheet(gray_rgb(out0[None, :]), edge(10), 0.44)
            a1 = mono("@ W1", size=22, color=ACCENT)
            a2 = mono("@ W2", size=22, color=GREEN)
            funnel = Group(v784, a1, v128, a2, v10).arrange(RIGHT, buff=0.5)
            funnel.move_to(UP * 1.15)

            frames = VGroup(*[framed(v, color=DIM) for v in (v784, v128, v10)])
            tags = VGroup(
                *[
                    mono(txt, size=19, color=col).next_to(v, DOWN, buff=0.22)
                    for txt, col, v in (
                        ("784 pixels", MUTED, v784),
                        ("128 hidden", ACCENT, v128),
                        ("10 outputs", GREEN, v10),
                    )
                ]
            )

            self.play(
                LaggedStart(
                    AnimationGroup(FadeIn(v784), Create(frames[0]), FadeIn(tags[0])),
                    FadeIn(a1, shift=RIGHT * 0.2),
                    AnimationGroup(FadeIn(v128), Create(frames[1]), FadeIn(tags[1])),
                    FadeIn(a2, shift=RIGHT * 0.2),
                    AnimationGroup(FadeIn(v10), Create(frames[2]), FadeIn(tags[2])),
                    lag_ratio=0.35,
                ),
                run_time=2.2,
            )

            outs = VGroup(*[neuron(radius=0.19, value=float(v)) for v in out0])
            outs.arrange(RIGHT, buff=0.2).move_to(DOWN * 0.9)
            digits = VGroup(
                *[
                    mono(str(i), size=20, color=MUTED).next_to(c, DOWN, buff=0.16)
                    for i, c in enumerate(outs)
                ]
            )
            fan_out = VGroup(
                *[
                    Line(v10.get_bottom(), c.get_top(), stroke_width=1,
                         stroke_color=GREEN, stroke_opacity=0.3)
                    for c in outs
                ]
            )
            self.play(
                Create(fan_out),
                FadeIn(outs, shift=DOWN * 0.25),
                FadeIn(digits, shift=UP * 0.1),
                run_time=1.2,
            )
            self.play(FadeIn(place_chips(chips("784 → 128 → 10", color=GREEN))), run_time=0.4)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        self.clear_out()
