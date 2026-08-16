import numpy as np
from manim import *
from network import init_params, forward

class Arkitektur(Scene):
    def construct(self):
        self.next_section()

        np.random.seed(42)
        sizes = [4, 5, 3, 2]
        Ws, bs = init_params(sizes)
        X = np.random.rand(1, sizes[0])
        A_out, Zs, As = forward(X, Ws, bs)

        # 1. Bygg nevronene
        layers = []
        for i, n in enumerate(sizes):
            col = VGroup(*[Circle(radius=0.25, color=RED, fill_opacity=1) for _ in range(n)])
            col.arrange(DOWN, buff=0.5)
            col.move_to(RIGHT * (i - 1.5) * 3)

            layers.append(col)
            self.play(FadeIn(col), run_time=0.3)

        self.wait(0.5)

        self.next_section()

        # 2. Color after activation
        for i, layer in enumerate(layers):
            curr_A = As[i]
            self.play(LaggedStart(*[n.animate.set_fill(RED, opacity=curr_A[0, j]) for j, n in enumerate(layer)], lag_ratio=0.1), run_time=0.3)

        color_map = color_gradient([BLUE, RED], 100)

        # 3. Draw connections
        lines = VGroup()
        for i in range(len(layers) - 1):
            for j, n1 in enumerate(layers[i]):   
                for k, n2 in enumerate(layers[i + 1]):
                    stroke_color = color_map[min(int((Ws[i][j, k] + 1) * 50), 99)]

                    line = Line(n1.get_right(), n2.get_left(), stroke_width=max(0.5, abs(Ws[i][j, k]) * 2), stroke_color=stroke_color)
                    lines.add(line)

        self.play(Create(lines), run_time=2)
        self.wait(1)
