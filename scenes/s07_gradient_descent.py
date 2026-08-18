"""Scene 7 — Gradient descent (4:35–5:15)."""

import numpy as np
from manim import *

from scenes.common import (
    ACCENT,
    DIM,
    FG,
    GOLD,
    GREEN,
    MUTED,
    Narrated3DScene,
    WARM,
    axis_ticks,
    body,
    chips,
    mono,
    place_chips,
    run,
)

# --- Landskapet i én vekt ----------------------------------------------------
# Kurven er ikke pyntet. Den starter i det ekte tapet fra scene 6 og bunner i
# tapet det samme bildet endte på etter trening, så y-aksen viser virkelige
# tall hele veien. Formen er en grunn parabel med litt skjevhet i, valgt slik
# at læringsrate 1.0 — den ekte, se nn/train.py — bruker ti synlige steg ned i
# bunnen. Da lyver ikke animasjonen om hverken tallene eller steglengden.
CURVE_A, CURVE_K, CURVE_W = 0.15, 1.1, 0.05
LR, LR_SMALL, LR_BIG = 1.0, 0.15, 7.0
STEPS = 10

_XS = np.linspace(-8, 8, 200_001)


def _raw(x):
    return CURVE_A * x**2 + CURVE_W * np.sin(CURVE_K * x)


_RAW_MIN = float(np.min(_raw(_XS)))
_X_MIN = float(_XS[np.argmin(_raw(_XS))])


def make_curve(loss_start: float, loss_floor: float):
    """f, f′, startpunkt og bunnpunkt, løftet slik at f(x0) er tapet før
    trening og bunnen er tapet etter."""
    offset = loss_floor - _RAW_MIN

    def f(x):
        return _raw(x) + offset

    def df(x):
        return 2 * CURVE_A * x + CURVE_W * CURVE_K * np.cos(CURVE_K * x)

    right = _XS[_XS > 0]
    x0 = float(right[np.argmin(np.abs(f(right) - loss_start))])
    return f, df, x0, _X_MIN


def descend(df, x0: float, lr: float, n: int) -> list[float]:
    xs, x = [x0], x0
    for _ in range(n):
        x = x - lr * df(x)
        xs.append(float(x))
    return xs


# --- Landskapet i to vekter --------------------------------------------------
SURF_A, SURF_S, SURF_K = 0.11, 0.35, 0.9
_UV = np.linspace(-4, 4, 401)
_SX, _SY = np.meshgrid(_UV, _UV)


def _raw2(x, y):
    return SURF_A * (x**2 + y**2) + SURF_S * np.sin(SURF_K * x) * np.cos(SURF_K * y)


_RAW2_MIN = float(np.min(_raw2(_SX, _SY)))


def make_surface(loss_floor: float):
    offset = loss_floor - _RAW2_MIN

    def f2(x, y):
        return _raw2(x, y) + offset

    def df2(x, y):
        return (
            2 * SURF_A * x + SURF_S * SURF_K * np.cos(SURF_K * x) * np.cos(SURF_K * y),
            2 * SURF_A * y - SURF_S * SURF_K * np.sin(SURF_K * x) * np.sin(SURF_K * y),
        )

    return f2, df2


# --- Tre læringsrater side om side -------------------------------------------
PANEL_X, PANEL_Y = 6.4, 5.5
PANEL_PLOT = 5.85  # der kurven treffer taket i ruta


def lr_panel(f, title: str, color) -> VGroup:
    axes = Axes(
        x_range=[-PANEL_X, PANEL_X, 2],
        y_range=[0, PANEL_Y, 1],
        x_length=3.9,
        y_length=2.3,
        tips=False,
        axis_config={"color": DIM, "stroke_width": 1.6},
    )
    curve = axes.plot(f, x_range=[-PANEL_PLOT, PANEL_PLOT], color=ACCENT, stroke_width=3)
    floor = Dot(axes.c2p(_X_MIN, f(_X_MIN)), color=GREEN, radius=0.05).set_opacity(0.8)
    label = mono(title, size=21, color=color).next_to(axes, UP, buff=0.22)
    group = VGroup(axes, curve, floor, label)
    group.axes = axes
    return group


def panel_point(axes: Axes, f, x: float) -> np.ndarray:
    """Punkt på kurven, klippet til ruta — en ball som stikker av skal vises
    på kanten, ikke tegnes ut i intet."""
    xc = float(np.clip(x, -PANEL_PLOT, PANEL_PLOT))
    return axes.c2p(xc, min(float(f(xc)), PANEL_Y - 0.08))


class S07GradientDescent(Narrated3DScene):
    def construct(self):
        data = run()
        n_weights = int(data["n_weights"])
        loss0 = float(data["untrained_loss"])
        loss_floor = float(data["trained_loss"])
        f, df, x0, x_min = make_curve(loss0, loss_floor)

        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[0, 3.2, 1],
            x_length=9.5,
            y_length=4.4,
            tips=False,
            axis_config={"color": DIM, "stroke_width": 2},
        )
        axes.move_to(DOWN * 0.25)
        # Tapet leses av på venstrekanten. Manims egen y-akse står i w = 0, midt
        # i bildet, og da ser tallene ute til venstre ut som om de svever.
        axes.y_axis.set_opacity(0)
        spine = Line(axes.c2p(-5, 0), axes.c2p(-5, 3.2), color=DIM, stroke_width=2)
        ticks = axis_ticks(axes, y_vals=(1, 2, 3), y_fmt="{:.0f}")
        x_lab = body(f"one weight — the other {n_weights - 1:,} held still", 21, MUTED)
        x_lab.next_to(axes, DOWN, buff=0.22).align_to(axes, RIGHT)
        y_lab = body("loss", 22, MUTED).rotate(PI / 2).next_to(spine, LEFT, buff=0.95)

        # --- Tapet fra forrige scene blir høyden i landskapet -----------------
        with self.narrate(
            "There are a hundred thousand weights in this network, and the loss depends on "
            "every single one of them."
        ) as t:
            carry = mono(f"loss = {loss0:.2f}", size=34, color=GOLD).move_to(UP * 0.5)
            self.play(FadeIn(carry, shift=DOWN * 0.2), run_time=0.6)

            self.cue(t, 0.30)
            start_tag = mono(f"{loss0:.2f}", size=22, color=GOLD)
            start_tag.next_to(axes.c2p(-5, loss0), LEFT, buff=0.16)
            self.play(
                Create(axes),
                Create(spine),
                FadeIn(ticks),
                FadeIn(y_lab),
                Transform(carry, start_tag),
                run_time=1.3,
            )

            self.cue(t, 0.58)
            ball = Dot(axes.c2p(x0, loss0), color=GOLD, radius=0.11)
            drop = DashedLine(
                axes.c2p(-5, loss0), axes.c2p(x0, loss0), color=GOLD, stroke_width=1.6
            ).set_opacity(0.45)
            self.play(Create(drop), run_time=0.6)
            self.play(FadeIn(ball, scale=0.4), FadeIn(x_lab), run_time=0.6)

            self.cue(t, 0.82)
            tags = place_chips(chips(f"{n_weights:,} parameters"))
            self.play(FadeIn(tags), run_time=0.6)

        # --- Landskapet ------------------------------------------------------
        with self.narrate(
            "Picture it as a landscape. Every position is one setting of all the weights, "
            "and the height is the loss. I want the bottom."
        ) as t:
            curve = axes.plot(f, x_range=[-4.72, 4.72], color=ACCENT, stroke_width=4)
            self.play(FadeOut(drop), Create(curve), run_time=2.6)

            self.cue(t, 0.50)
            target = Circle(radius=0.17, color=GREEN, stroke_width=3)
            target.move_to(axes.c2p(x_min, loss_floor))
            floor_tag = mono(f"{loss_floor:.2f}", size=22, color=GREEN)
            floor_tag.next_to(axes.c2p(-5, loss_floor), LEFT, buff=0.16)
            self.play(Create(target), FadeIn(floor_tag), run_time=0.8)

            self.cue(t, 0.74)
            note = body("where training actually ended up", 20, GREEN)
            note.next_to(target, UP, buff=0.35).shift(RIGHT * 1.5)
            hint = Line(note.get_left() + LEFT * 0.12, target.get_right() + RIGHT * 0.06,
                        color=GREEN, stroke_width=1.6).set_opacity(0.5)
            self.play(FadeIn(note), Create(hint), run_time=0.7)

        # --- Stigningen, og ett steg i sakte film -----------------------------
        with self.narrate(
            "I can't see this landscape — it has a hundred thousand dimensions. But wherever "
            "I stand, I can measure the slope for every weight at once. That's the gradient. "
            "So: small step downhill, and repeat."
        ) as t:
            self.play(FadeOut(note), FadeOut(hint), run_time=0.4)

            xt = ValueTracker(x0)
            step_no = ValueTracker(0)
            ball.add_updater(lambda m: m.move_to(axes.c2p(xt.get_value(), f(xt.get_value()))))

            def tangent():
                x = xt.get_value()
                here = axes.c2p(x, f(x))
                along = axes.c2p(x + 1, f(x) + df(x)) - here
                along = along / np.linalg.norm(along) * 1.0
                return Line(here - along, here + along, color=WARM, stroke_width=4)

            tan_seed = tangent()
            self.play(Create(tan_seed), run_time=0.7)
            self.remove(tan_seed)
            tan = always_redraw(tangent)
            self.add(tan)

            # HUD oppe til høyre — faste ankere, så tallene ikke hopper sidelengs
            def hud(i, fn, color):
                y = 3.45 - i * 0.44
                return always_redraw(
                    lambda: mono(fn(), size=22, color=color).move_to(
                        np.array([4.35, y, 0]), aligned_edge=LEFT
                    )
                )

            hud_step = hud(0, lambda: f"step  {int(step_no.get_value()):>2d}", MUTED)
            hud_loss = hud(1, lambda: f"loss  {f(xt.get_value()):.2f}", GOLD)
            hud_slope = hud(2, lambda: f"slope {df(xt.get_value()):+.2f}", WARM)
            self.play(FadeIn(VGroup(hud_step, hud_loss, hud_slope)), run_time=0.5)

            # Stå et annet sted, og tallene er andre. Det er hele poenget med
            # at stigningen måles der man er.
            self.play(xt.animate.set_value(3.15), run_time=1.0, rate_func=smooth)
            self.play(xt.animate.set_value(x0), run_time=0.9, rate_func=smooth)

            rule = mono("w  ←  w  −  lr × slope", size=27, color=FG).to_corner(UL, buff=0.6)
            lr_tag = mono(f"lr = {LR:.1f}", size=22, color=GOLD).next_to(rule, DOWN, buff=0.22)
            lr_tag.align_to(rule, LEFT)
            self.cue(t, 0.30)
            self.play(FadeIn(rule, shift=DOWN * 0.15), FadeIn(lr_tag), run_time=0.7)

            path = descend(df, x0, LR, STEPS)

            # Første steg i sakte film: pila er nøyaktig lr × stigningen, og
            # ballen faller ned på kurven der pila peker.
            self.cue(t, 0.52)
            arrow = Arrow(
                axes.c2p(x0, loss0),
                axes.c2p(path[1], loss0),
                buff=0,
                color=GOLD,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.12,
            )
            arrow_tag = mono(f"Δw = −{LR:.1f} × {df(x0):.2f}", size=20, color=GOLD)
            arrow_tag.next_to(arrow, UP, buff=0.12)
            fall = DashedLine(
                axes.c2p(path[1], loss0), axes.c2p(path[1], f(path[1])),
                color=GOLD, stroke_width=1.8,
            ).set_opacity(0.5)
            self.play(GrowArrow(arrow), FadeIn(arrow_tag), run_time=0.6)
            self.play(Create(fall), run_time=0.4)
            self.play(
                xt.animate.set_value(path[1]),
                step_no.animate.set_value(1),
                run_time=0.5,
            )
            self.play(FadeOut(VGroup(arrow, arrow_tag, fall)), run_time=0.3)

            # Resten: samme steg om og om igjen. Spøkelsene blir liggende, så
            # man ser at stegene krymper av seg selv når bakken flater ut.
            self.cue(t, 0.66)
            ghosts = VGroup()
            for i, nxt in enumerate(path[2:], start=2):
                ghost = Dot(ball.get_center(), color=GOLD, radius=0.055).set_opacity(0.3)
                ghosts.add(ghost)
                self.add(ghost)
                self.play(
                    xt.animate.set_value(nxt),
                    step_no.animate.set_value(i),
                    run_time=0.3,
                    rate_func=smooth,
                )

            shrink = body("the flatter it gets, the smaller the steps", 20, MUTED)
            shrink.move_to(axes.c2p(0, 1.75))
            self.play(FadeIn(shrink), Flash(target, color=GREEN, line_length=0.18), run_time=0.7)
            self.remove(tan)

        # --- For stort, for lite, akkurat passe ------------------------------
        with self.narrate(
            "Too big a step and you fly over the valley, and end up worse than you started. "
            "Too small and you're there all week. That's the learning rate — mine is one, "
            "found by trying."
        ) as t:
            self.play(
                FadeOut(VGroup(axes, spine, curve, ticks, x_lab, y_lab, target, shrink, rule, lr_tag)),
                FadeOut(VGroup(carry, floor_tag, tags, ball, ghosts, hud_step, hud_loss, hud_slope)),
                run_time=0.6,
            )

            specs = [
                (LR_SMALL, "lr = 0.15", MUTED, "barely moved"),
                (LR, "lr = 1.0", GREEN, "there"),
                (LR_BIG, "lr = 7.0", WARM, "worse every step"),
            ]
            panels = VGroup(*[lr_panel(f, title, color) for _, title, color, _ in specs])
            panels.arrange(RIGHT, buff=0.5).move_to(UP * 0.25)
            header = body("same curve, same starting point, three step sizes", 22, MUTED)
            header.to_edge(UP, buff=0.75)
            self.play(FadeIn(header), run_time=0.4)
            self.play(
                LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in panels], lag_ratio=0.15),
                run_time=1.0,
            )

            paths = [descend(df, x0, lr, STEPS) for lr, _, _, _ in specs]
            dots = VGroup(
                *[
                    Dot(panel_point(p.axes, f, x0), color=GOLD, radius=0.085)
                    for p in panels
                ]
            )
            reads = VGroup(
                *[
                    mono(f"{loss0:.2f}", size=21, color=GOLD).next_to(p, DOWN, buff=0.22)
                    for p in panels
                ]
            )
            self.play(FadeIn(dots), FadeIn(reads), run_time=0.5)

            self.cue(t, 0.30)
            trace = VGroup()   # spøkelser og sikksakk, så de kan tones ut samlet
            escaped = [False] * len(specs)
            for i in range(1, STEPS + 1):
                moves = []
                for j, (panel, walk) in enumerate(zip(panels, paths)):
                    if escaped[j]:
                        continue
                    x_now, x_next = walk[i - 1], walk[i]
                    ghost = Dot(dots[j].get_center(), color=GOLD, radius=0.045).set_opacity(0.3)
                    trace.add(ghost)
                    self.add(ghost)
                    if abs(x_next) > PANEL_PLOT:
                        # Ute av ruta: opp og ut, og så er den borte.
                        escaped[j] = True
                        out = panel.axes.c2p(np.sign(x_next) * PANEL_PLOT, PANEL_Y + 0.9)
                        moves.append(dots[j].animate.move_to(out).set_opacity(0))
                        moves.append(
                            Transform(
                                reads[j],
                                mono("off the map", size=21, color=WARM).move_to(reads[j]),
                            )
                        )
                    else:
                        moves.append(dots[j].animate.move_to(panel_point(panel.axes, f, x_next)))
                        colour = WARM if f(x_next) > f(x_now) else GOLD
                        moves.append(
                            Transform(
                                reads[j],
                                mono(f"{f(x_next):.2f}", size=21, color=colour).move_to(reads[j]),
                            )
                        )
                    # sikksakken over dalen er hele poenget med for stor lr
                    if abs(x_next - x_now) > 2.0:
                        hop = Line(
                            panel_point(panel.axes, f, x_now),
                            panel_point(panel.axes, f, x_next),
                            color=WARM,
                            stroke_width=1.8,
                        ).set_opacity(0.55)
                        trace.add(hop)
                        moves.append(Create(hop))
                if not moves:
                    break
                self.play(*moves, run_time=0.42)

            self.cue(t, 0.72)
            verdicts = VGroup(
                *[
                    mono(word, size=20, color=color).next_to(reads[j], DOWN, buff=0.18)
                    for j, (_, _, color, word) in enumerate(specs)
                ]
            )
            self.play(
                LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in verdicts], lag_ratio=0.2),
                run_time=0.9,
            )

            self.cue(t, 0.88)
            code = place_chips(chips(f"learning rate = {LR:.1f}", "W -= lr * dW"))
            self.play(FadeIn(code), run_time=0.5)

        # --- Og så i flere dimensjoner ---------------------------------------
        with self.narrate(
            "That's one weight. Here are two — a whole landscape to walk down. "
            f"Now imagine {n_weights:,} of them."
        ) as t:
            self.play(FadeOut(VGroup(panels, dots, reads, verdicts, code, header, trace)), run_time=0.6)
            for m in list(self.mobjects):
                self.remove(m)

            f2, df2 = make_surface(loss_floor)
            axes3 = ThreeDAxes(
                x_range=[-4, 4, 2],
                y_range=[-4, 4, 2],
                z_range=[0, 4, 1],
                x_length=6.5,
                y_length=6.5,
                z_length=2.8,
                axis_config={"color": DIM, "stroke_width": 2},
            )
            axes3.shift(DOWN * 0.3)
            surface = Surface(
                lambda u, v: axes3.c2p(u, v, f2(u, v)),
                u_range=[-4, 4],
                v_range=[-4, 4],
                resolution=(30, 30),
                fill_opacity=0.72,
                stroke_width=0.4,
                stroke_color=DIM,
                checkerboard_colors=[ManimColor("#1f3d6b"), ManimColor("#2e5b9e")],
            )

            self.set_camera_orientation(phi=62 * DEGREES, theta=-52 * DEGREES, zoom=0.95)
            self.play(FadeIn(axes3), run_time=0.5)

            # Uten navn på aksene leses flaten bare som en pen 3D-graf. Med navn
            # er den poenget: én akse per vekt, høyden er tapet.
            lab_x = mono("weight 1", 20, MUTED).move_to(axes3.c2p(5.6, -1.0, 0.2))
            lab_y = mono("weight 2", 20, MUTED).move_to(axes3.c2p(-0.6, -5.6, 0.2))
            lab_z = mono("loss", 20, GOLD).move_to(axes3.c2p(0, 0, 4.9))
            self.add_fixed_orientation_mobjects(lab_x, lab_y, lab_z)
            self.play(FadeIn(VGroup(lab_x, lab_y, lab_z)), run_time=0.4)
            self.play(Create(surface), run_time=1.8)

            # ekte gradient descent på flaten — samme regel, én dimensjon til
            p = np.array([3.8, 3.6])
            walk = [p.copy()]
            for _ in range(60):
                gx, gy = df2(p[0], p[1])
                p = np.clip(p - 0.9 * np.array([gx, gy]), -4, 4)
                walk.append(p.copy())

            trail = VMobject(color=GOLD, stroke_width=5)
            trail.set_points_smoothly([axes3.c2p(x, y, f2(x, y) + 0.12) for x, y in walk])
            marble = Dot3D(
                point=axes3.c2p(*walk[0], f2(*walk[0]) + 0.12), color=GOLD, radius=0.09
            )
            self.add(marble)
            self.begin_ambient_camera_rotation(rate=0.06)
            self.cue(t, 0.45)
            self.play(
                Create(trail), MoveAlongPath(marble, trail), run_time=2.4, rate_func=linear
            )

            caption = mono(f"now imagine {n_weights:,} dimensions", size=28, color=GOLD)
            caption.to_edge(DOWN, buff=0.6)
            self.add_fixed_in_frame_mobjects(caption)
            self.cue(t, 0.85)
            self.play(FadeIn(caption), run_time=0.7)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.4))
            self.stop_ambient_camera_rotation()

        self.clear_out()
