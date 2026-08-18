"""Live-visning av første lags vekter mens nettverket trener.

    make train-live        (eller: LIVE=1 python -m nn.train)

De 128 nevronene tegnes som et 8x16-ark av 28x28-bilder som oppdateres
underveis. To ting avgjør om dette er brukbart:

* Ett enkelt AxesImage som oppdateres med set_data. Kaller man imshow på nytt
  for hver oppdatering bygges figuren opp igjen fra bunnen, og treningen blir
  mangedobbelt tregere enn selve regnestykket.
* Fast fargeskala. Normaliserer man hver oppdatering for seg, flimrer bildet og
  man ser ikke det eneste man er ute etter: at vektene faktisk vokser. Skalaen
  her settes fra startvektene og får bare lov til å øke.
"""

from __future__ import annotations

import numpy as np


class LiveWeights:
    def __init__(self, rows: int = 8, cols: int = 16, every: int = 50, gap: int = 1):
        import matplotlib.pyplot as plt

        self.plt = plt
        self.rows, self.cols, self.gap, self.every = rows, cols, gap, every
        self.vmax = None
        self.im = None

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(9, 4.8))
        self.ax.set_axis_off()
        self.fig.tight_layout()

    def _sheet(self, W: np.ndarray) -> np.ndarray:
        h = self.rows * 28 + (self.rows - 1) * self.gap
        w = self.cols * 28 + (self.cols - 1) * self.gap
        canvas = np.full((h, w), np.nan, dtype=np.float32)  # nan = mellomrom
        for k in range(min(W.shape[1], self.rows * self.cols)):
            r, c = divmod(k, self.cols)
            y, x = r * (28 + self.gap), c * (28 + self.gap)
            canvas[y : y + 28, x : x + 28] = W[:, k].reshape(28, 28)
        return canvas

    def update(self, W: np.ndarray, step: int, extra: str = "") -> None:
        if step % self.every and self.im is not None:
            return

        sheet = self._sheet(W)
        scale = float(np.nanpercentile(np.abs(sheet), 99.5))
        self.vmax = scale if self.vmax is None else max(self.vmax, scale)

        if self.im is None:
            cmap = self.plt.get_cmap("RdBu_r").copy()
            cmap.set_bad("#0d1117")  # mellomrommene mellom feltene
            self.im = self.ax.imshow(
                sheet, cmap=cmap, vmin=-self.vmax, vmax=self.vmax, interpolation="nearest"
            )
        else:
            self.im.set_data(sheet)
            self.im.set_clim(-self.vmax, self.vmax)

        self.ax.set_title(f"W1 — batch {step:,}{extra}", fontsize=10)
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def keep_open(self) -> None:
        self.plt.ioff()
        self.plt.show()
