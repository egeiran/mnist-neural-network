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


def f(x):
    return 0.22 * x**2 + 0.45 * np.sin(1.6 * x) + 1.2


def df(x):
    return 0.44 * x + 0.72 * np.cos(1.6 * x)


def f2(x, y):
    return 0.13 * (x**2 + y**2) + 0.55 * np.sin(1.1 * x) * np.cos(1.1 * y) + 1.0


def df2(x, y):
    return (
        0.26 * x + 0.605 * np.cos(1.1 * x) * np.cos(1.1 * y),
        0.26 * y - 0.605 * np.sin(1.1 * x) * np.sin(1.1 * y),
    )


class S07GradientDescent(Narrated3DScene):
    def construct(self):
        data = run()
        n_weights = int(data["n_weights"])

        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[0, 7, 1],
            x_length=9.5,
            y_length=4.6,
            tips=False,
            axis_config={"color": DIM, "stroke_width": 2},
        )
        axes.move_to(DOWN * 0.4)
        curve = axes.plot(f, x_range=[-4.6, 4.6], color=ACCENT, stroke_width=4)
        x_lab = body("one weight", 22, MUTED).next_to(axes, DOWN, buff=0.25).align_to(axes, RIGHT)
        y_lab = body("loss", 22, MUTED).rotate(PI / 2).next_to(axes, LEFT, buff=0.2)

        with self.narrate(
            "There are a hundred thousand weights in this network, and the loss depends on "
            "every single one of them."
        ) as t:
            self.play(Create(axes), FadeIn(x_lab), FadeIn(y_lab), run_time=1.0)
            tags = place_chips(chips(f"{n_weights:,} parameters", "learning rate = 1.0"))
            self.play(FadeIn(tags), run_time=0.6)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Picture it as a landscape. Every position is one setting of all the weights, "
            "and the height is the loss. I want the bottom of the valley."
        ) as t:
            self.play(Create(curve), run_time=1.6)
            x0 = 4.1
            ball = Dot(axes.c2p(x0, f(x0)), color=GOLD, radius=0.12)
            self.play(FadeIn(ball, scale=0.5), run_time=0.5)

            bottom = float(np.min([f(v) for v in np.linspace(-4.6, 4.6, 2000)]))
            xb = float(np.linspace(-4.6, 4.6, 2000)[np.argmin([f(v) for v in np.linspace(-4.6, 4.6, 2000)])])
            target = Circle(radius=0.18, color=GREEN, stroke_width=3).move_to(axes.c2p(xb, bottom))
            self.play(Create(target), run_time=0.6)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "I can't see the landscape — it has a hundred thousand dimensions. But I can feel "
            "the slope under my feet. So I take a small step downhill, and repeat."
        ) as t:
            cur = [x0]
            slope_line = always_redraw(
                lambda: Line(
                    axes.c2p(cur[0] - 0.9, f(cur[0]) - 0.9 * df(cur[0])),
                    axes.c2p(cur[0] + 0.9, f(cur[0]) + 0.9 * df(cur[0])),
                    color=WARM,
                    stroke_width=4,
                )
            )
            self.add(slope_line)
            self.play(Create(slope_line), run_time=0.6)

            lr = 0.55
            steps = mono("step 0", size=22, color=GOLD).to_corner(UR, buff=0.7)
            self.add(steps)
            for i in range(9):
                nxt = cur[0] - lr * df(cur[0])
                new_steps = mono(f"step {i + 1}", size=22, color=GOLD).to_corner(UR, buff=0.7)
                self.play(
                    ball.animate.move_to(axes.c2p(nxt, f(nxt))),
                    UpdateFromFunc(steps, lambda m, s=new_steps: m.become(s)),
                    run_time=0.32,
                    rate_func=rush_into if i == 0 else smooth,
                )
                cur[0] = nxt
            self.remove(slope_line)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        with self.narrate(
            "Step too big and you fly straight over the valley and end up worse than you "
            "started. Step too small and you're there all week. That's the learning rate, "
            "and mostly you find it by trying."
        ) as t:
            self.play(FadeOut(steps), run_time=0.3)
            big = mono("learning rate too big", size=26, color=WARM).to_edge(UP, buff=0.6)
            self.play(ball.animate.move_to(axes.c2p(x0, f(x0))), FadeIn(big), run_time=0.7)

            lr_big = 2.6
            x = x0
            for _ in range(5):
                nxt = x - lr_big * df(x)
                if abs(nxt) > 4.6:
                    nxt = np.sign(nxt) * 5.6
                    self.play(ball.animate.move_to(axes.c2p(nxt, 7.5)), run_time=0.45)
                    break
                self.play(ball.animate.move_to(axes.c2p(nxt, f(nxt))), run_time=0.45)
                x = nxt
            self.play(FadeOut(ball), run_time=0.3)

            small = mono("learning rate too small", size=26, color=MUTED).to_edge(UP, buff=0.6)
            self.play(Transform(big, small), run_time=0.5)
            ball2 = Dot(axes.c2p(x0, f(x0)), color=GOLD, radius=0.12)
            self.play(FadeIn(ball2), run_time=0.3)
            x = x0
            for _ in range(8):
                x = x - 0.06 * df(x)
                self.play(ball2.animate.move_to(axes.c2p(x, f(x))), run_time=0.16)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.1))

        # --- Og så i flere dimensjoner ---------------------------------------
        with self.narrate(
            "That's one weight. Here are two — a whole landscape to walk down. "
            f"Now imagine {n_weights:,} of them."
        ) as t:
            self.play(
                FadeOut(VGroup(axes, curve, x_lab, y_lab, target, big, ball2, tags)),
                run_time=0.7,
            )

            axes3 = ThreeDAxes(
                x_range=[-4, 4, 2],
                y_range=[-4, 4, 2],
                z_range=[0, 6, 2],
                x_length=6.5,
                y_length=6.5,
                z_length=3.0,
                axis_config={"color": DIM, "stroke_width": 2},
            )
            surface = Surface(
                lambda u, v: axes3.c2p(u, v, f2(u, v)),
                u_range=[-4, 4],
                v_range=[-4, 4],
                resolution=(28, 28),
                fill_opacity=0.72,
                stroke_width=0.4,
                stroke_color=DIM,
                checkerboard_colors=[ManimColor("#1f3d6b"), ManimColor("#2e5b9e")],
            )

            axes3.shift(DOWN * 0.35)
            self.set_camera_orientation(phi=64 * DEGREES, theta=-55 * DEGREES, zoom=0.85)
            self.play(FadeIn(axes3), run_time=0.6)
            self.play(Create(surface), run_time=2.0)

            # ekte gradient descent på flaten
            p = np.array([3.6, 3.4])
            path_pts = [p.copy()]
            for _ in range(70):
                gx, gy = df2(p[0], p[1])
                p = p - 0.17 * np.array([gx, gy])
                p = np.clip(p, -4, 4)
                path_pts.append(p.copy())

            trail = VMobject(color=GOLD, stroke_width=5)
            trail.set_points_smoothly(
                [axes3.c2p(x, y, f2(x, y) + 0.14) for x, y in path_pts]
            )
            marble = Dot3D(
                point=axes3.c2p(*path_pts[0], f2(*path_pts[0]) + 0.14),
                color=GOLD,
                radius=0.09,
            )
            self.add(marble)
            self.begin_ambient_camera_rotation(rate=0.06)
            self.play(
                Create(trail),
                MoveAlongPath(marble, trail),
                run_time=2.6,
                rate_func=linear,
            )

            caption = mono(f"now imagine {n_weights:,} dimensions", size=28, color=GOLD)
            caption.to_edge(DOWN, buff=0.7)
            self.add_fixed_in_frame_mobjects(caption)
            self.play(FadeIn(caption), run_time=0.8)
            self.wait(max(t.get_remaining_duration() - 0.2, 0.4))
            self.stop_ambient_camera_rotation()

        self.clear_out()
