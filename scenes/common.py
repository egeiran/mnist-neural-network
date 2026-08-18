"""Felles stil, data og fortellerstemme for alle scenene.

Alle scener arver fra NarratedScene / Narrated3DScene og bruker `self.narrate(...)`
rundt animasjonene sine. Uten VOICEOVER=1 estimeres lengden på hver replikk ut fra
teksten, slik at hele filmen kan rendres uten å røre ElevenLabs-APIet. Med
VOICEOVER=1 byttes den samme blokken ut med ekte manim-voiceover.
"""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parent.parent

# --- Voiceover av/på ---------------------------------------------------------
USE_VOICE = os.environ.get("VOICEOVER", "0").lower() not in ("0", "", "false", "no")

# --- Palett ------------------------------------------------------------------
BG = "#0d1117"
FG = "#e6edf3"
MUTED = "#8b949e"
DIM = "#30363d"
ACCENT = "#58a6ff"   # blå — nettverk, aktivering
WARM = "#ff7b72"     # rød — feil, gradienter
GOLD = "#f0b429"     # gul — tall som betyr noe
GREEN = "#3fb950"    # grønn — riktig
VIOLET = "#bc8cff"

FONT = "Helvetica Neue"
MONO = "Menlo"

config.background_color = BG

POS = ManimColor(ACCENT)
NEG = ManimColor(WARM)


# --- Tekst-hjelpere ----------------------------------------------------------
def body(text: str, size: float = 34, color: str = FG, weight=NORMAL, **kw) -> Text:
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kw)


def mono(text: str, size: float = 28, color: str = FG, **kw) -> Text:
    return Text(text, font=MONO, font_size=size, color=color, **kw)


def formula(text: str, size: float = 36, color: str = FG, **kw) -> Text:
    """Formler settes i monospace — vi har ingen LaTeX på denne maskinen,
    og monospace kler et 'jeg skrev dette selv'-prosjekt uansett."""
    return Text(text, font=MONO, font_size=size, color=color, **kw)


def chip(text: str, color: str = MUTED, size: float = 24) -> VGroup:
    """Liten etikett nede til venstre — manusets 'on-screen'-tekst.

    Streken til venstre måles ut fra tekststørrelsen, ikke fra tekstens
    tilfeldige høyde, slik at alle chips får nøyaktig like lange streker
    uansett om ordene har staver og haler i seg."""
    label = mono(text, size=size, color=color)
    bar = Line(UP * size * 0.0075, DOWN * size * 0.0075, color=color, stroke_width=2.5)
    bar.set_cap_style(CapStyleType.ROUND)
    bar.set_stroke(opacity=0.45)
    bar.next_to(label, LEFT, buff=size * 0.013)
    bar.align_to(label, UP)
    return VGroup(bar, label)


def chips(*texts: str, color: str = MUTED, size: float = 24) -> VGroup:
    group = VGroup(*[chip(t, color=color, size=size) for t in texts])
    group.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
    return group


def place_chips(group: VGroup) -> VGroup:
    return group.to_corner(DL, buff=0.55)


def backdrop(mobj: Mobject, opacity: float = 0.88, buff: float = 0.25) -> VGroup:
    """Legger en dempet bakgrunnsplate bak tekst som ligger oppå annen grafikk."""
    rect = BackgroundRectangle(mobj, color=ManimColor(BG), fill_opacity=opacity, buff=buff)
    return VGroup(rect, mobj)


# --- MNIST-hjelpere ----------------------------------------------------------
def digit_image(vec: np.ndarray, height: float = 4.0) -> ImageMobject:
    """28x28-vektor (0–1) som skarp bildeflate."""
    arr = (np.clip(vec.reshape(28, 28), 0, 1) * 255).astype(np.uint8)
    img = ImageMobject(arr)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    img.height = height
    return img


def tile_images(vecs: np.ndarray, cols: int, shape=(28, 28)) -> np.ndarray:
    """Setter mange bilder sammen til ett stort bilde — mye raskere å tegne
    enn hundre separate ImageMobjects."""
    n = len(vecs)
    rows = int(np.ceil(n / cols))
    h, w = shape
    canvas = np.zeros((rows * h, cols * w), dtype=np.uint8)
    for i, v in enumerate(vecs):
        r, c = divmod(i, cols)
        tile = np.clip(v.reshape(h, w), 0, 1)
        canvas[r * h : (r + 1) * h, c * w : (c + 1) * w] = (tile * 255).astype(np.uint8)
    return canvas


def image_from_array(arr: np.ndarray, height: float) -> ImageMobject:
    img = ImageMobject(arr)
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    img.height = height
    return img


def normalize_signed(arr: np.ndarray) -> np.ndarray:
    """Vekter kan være negative — skaler symmetrisk til 0–1 for visning."""
    m = np.max(np.abs(arr))
    if m == 0:
        return np.full_like(arr, 0.5)
    return (arr / m + 1) / 2


def signed_rgb(M: np.ndarray, gamma: float = 0.45, scale: float | None = None) -> np.ndarray:
    """Vektmatrise → RGB: blått for positivt, rødt for negativt.

    scale=None normaliserer hver matrise for seg. Skal flere bilder sammenlignes
    — nabofelt i et ark, eller samme felt over tid — må de dele én fast skala,
    ellers flimrer kontrasten og man ser ikke at vektene faktisk vokser.
    """
    if scale is None:
        scale = np.percentile(np.abs(M), 99.0)
    scale = float(scale) + 1e-12
    n = np.clip(M / scale, -1, 1)
    pos = np.clip(n, 0, 1) ** gamma
    neg = np.clip(-n, 0, 1) ** gamma
    blue = np.array(ManimColor(ACCENT).to_rgb())
    red = np.array(ManimColor(WARM).to_rgb())
    rgb = pos[..., None] * blue + neg[..., None] * red
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def weight_sheet(
    W: np.ndarray,
    rows: int = 8,
    cols: int = 16,
    gap: int = 2,
    scale: float | None = None,
) -> np.ndarray:
    """Første lags vekter → ett ark: hver kolonne i W er ett nevron, brettet
    tilbake til 28×28. W har form (784, n_nevroner)."""
    h = rows * 28 + (rows - 1) * gap
    w = cols * 28 + (cols - 1) * gap
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    canvas[:, :] = (np.array(ManimColor(BG).to_rgb()) * 255).astype(np.uint8)
    for k in range(min(W.shape[1], rows * cols)):
        r, c = divmod(k, cols)
        tile = signed_rgb(W[:, k].reshape(28, 28), scale=scale)
        y, x = r * (28 + gap), c * (28 + gap)
        canvas[y : y + 28, x : x + 28] = tile
    return canvas


def weight_scale(W: np.ndarray, pct: float = 99.5) -> float:
    """Én fast fargeskala for et helt ark / en hel tidsserie."""
    return float(np.percentile(np.abs(np.asarray(W, dtype=np.float32)), pct))


def pixel_grid(vec: np.ndarray, cell: float = 0.16, stroke: float = 0.6) -> VGroup:
    """28x28 ruter med synlige rutelinjer."""
    grid = VGroup()
    img = np.clip(vec.reshape(28, 28), 0, 1)
    for r in range(28):
        for c in range(28):
            sq = Square(
                side_length=cell,
                fill_color=WHITE,
                fill_opacity=float(img[r, c]),
                stroke_color=DIM,
                stroke_width=stroke,
            )
            sq.move_to(np.array([(c - 13.5) * cell, (13.5 - r) * cell, 0]))
            grid.add(sq)
    return grid


def axis_ticks(
    axes: Axes,
    x_vals=(),
    y_vals=(),
    size: float = 18,
    color: str = MUTED,
    x_fmt: str = "{:.0f}",
    y_fmt: str = "{:.1f}",
) -> VGroup:
    """Akse-tall som Text — manim sine include_numbers krever LaTeX, som vi ikke har."""
    g = VGroup()
    x0 = axes.x_range[0]
    y0 = axes.y_range[0]
    for x in x_vals:
        g.add(mono(x_fmt.format(x), size, color).next_to(axes.c2p(x, y0), DOWN, buff=0.16))
    for y in y_vals:
        g.add(mono(y_fmt.format(y), size, color).next_to(axes.c2p(x0, y), LEFT, buff=0.16))
    return g


def neuron(radius: float = 0.22, value: float = 0.0, color: str = ACCENT) -> Circle:
    return Circle(
        radius=radius,
        stroke_color=MUTED,
        stroke_width=1.5,
        fill_color=color,
        fill_opacity=float(np.clip(value, 0, 1)),
    )


def _column_indices(values: np.ndarray, n_top: int, n_mid: int, n_bottom: int) -> list[list[int]]:
    """Hvilke av de 784 tallene vi faktisk tegner: noen i toppen, en stripe midt
    i sifferet (der det er blekk å se), og noen i bunnen. Indeksene er ekte —
    midtstripa legges rundt den lyseste pikselen."""
    n = len(values)
    top = list(range(n_top))
    bottom = list(range(n - n_bottom, n))
    lo, hi = n_top + 1, n - n_bottom - n_mid - 1
    start = int(np.clip(int(np.argmax(values)) - n_mid // 2, lo, hi))
    return [top, list(range(start, start + n_mid)), bottom]


def _vdots(radius: float, color: str = MUTED) -> VGroup:
    dots = VGroup(*[Dot(radius=max(radius * 0.16, 0.018), color=color) for _ in range(3)])
    return dots.arrange(DOWN, buff=radius * 0.55)


def node_column(
    values: np.ndarray,
    n_top: int = 4,
    n_mid: int = 4,
    n_bottom: int = 3,
    radius: float = 0.12,
    buff: float = 0.16,
    color: str = WHITE,
    fill: bool = True,
    labels: bool = False,
    label_size: float = 15,
    height: float | None = None,
) -> VGroup:
    """En lang vektor tegnet som noder: noen noder, ⋮, noen noder, ⋮, noen noder.

    Hver node fylles etter verdien sin, akkurat som pikselen den kommer fra.
    `fill=False` tegner dem tomme, men tar vare på verdiene i `values`, slik at
    en scene kan tenne dem senere. Gruppa får med seg `nodes`, `indices`,
    `values`, `entries` (noden med etikettene sine) og `y_of(i)` — høyden en
    vilkårlig vektorindeks ville hatt i kolonnen, slik at animasjoner kan lande
    der tallet hører hjemme."""
    vals = np.asarray(values, dtype=np.float64).reshape(-1)
    groups = _column_indices(vals, n_top, n_mid, n_bottom)

    step = 2 * radius + buff
    nodes, entries, dots = VGroup(), [], VGroup()
    indices, shown_values, dot_indices = [], [], []
    idx_labels, val_labels = [], []

    y = 0.0
    for gi, group in enumerate(groups):
        if gi:
            d = _vdots(radius).move_to(np.array([0.0, y - step * 0.15, 0.0]))
            dots.add(d)
            dot_indices.append((groups[gi - 1][-1] + group[0]) / 2)
            y -= step * 1.3
        for i in group:
            v = float(np.clip(vals[i], 0, 1))
            node = neuron(radius=radius, value=v if fill else 0.0, color=color)
            node.move_to(np.array([0.0, y, 0.0]))
            nodes.add(node)
            indices.append(int(i))
            shown_values.append(v)
            entry = node
            if labels:
                entry = VGroup(node)
                lab_i = mono(f"x[{i}]", size=label_size, color=DIM)
                lab_v = mono(f"{v:.2f}", size=label_size, color=GOLD if v > 0.01 else MUTED)
                idx_labels.append(lab_i)
                val_labels.append(lab_v)
                entry.add(lab_i, lab_v)
            entries.append(entry)
            y -= step

    if labels:
        # next_to legger høyre kant av indeksen og venstre kant av verdien mot
        # noden, så begge spaltene står rett uansett hvor mange sifre de har.
        gap = radius + 0.16
        for node, lab_i, lab_v in zip(nodes, idx_labels, val_labels):
            lab_i.next_to(node, LEFT, buff=gap)
            lab_v.next_to(node, RIGHT, buff=gap)

    group_all = VGroup(*entries, dots)
    group_all.move_to(ORIGIN)
    if height is not None:
        group_all.scale(height / group_all.height)

    def y_of(i: float) -> float:
        xs = np.array(indices, dtype=float)
        ys = np.array([n.get_center()[1] for n in nodes])
        return float(np.interp(float(i), xs, ys))

    group_all.nodes = nodes
    group_all.entries = VGroup(*entries)
    group_all.dots = dots
    group_all.indices = indices
    group_all.values = shown_values
    group_all.dot_indices = dot_indices
    group_all.y_of = y_of
    return group_all


# --- Data --------------------------------------------------------------------
_RUN = None


def run():
    """Alt scenene viser av tall kommer herfra (artifacts/run.npz)."""
    global _RUN
    if _RUN is None:
        path = ROOT / "artifacts" / "run.npz"
        if not path.exists():
            raise FileNotFoundError(f"Mangler {path}. Kjør `make artifacts` først.")
        _RUN = np.load(path, allow_pickle=False)
    return _RUN


# --- Fortellerstemme ---------------------------------------------------------
_BOOKMARK = re.compile(r"<bookmark\s*mark\s*=\s*['\"](.*?)['\"]\s*/>")

WORDS_PER_SEC = 2.75
SENTENCE_PAUSE = 0.45
COMMA_PAUSE = 0.15

# --- Rask forhåndsvisning ----------------------------------------------------
# Det meste av en scenes lengde er ventetid mens den tenkte fortellerstemmen
# snakker. FAST=1 estimerer narrasjonen til en firedel, så scenen rendres på en
# brøkdel av tiden. SPEED=0.5 gir finkontroll (1.0 = ekte lengde). Timingen blir
# da ikke filmens timing — bruk det til å se på grafikken, ikke på rytmen. Med
# ekte voiceover ignoreres begge: lyden har den lengden den har.


def _narration_scale() -> float:
    if USE_VOICE:
        return 1.0
    raw = os.environ.get("SPEED", "").strip()
    if raw:
        return max(float(raw), 0.02)
    if os.environ.get("FAST", "0").lower() not in ("0", "", "false", "no"):
        return 0.25
    return 1.0


NARRATION_SCALE = _narration_scale()
FAST_PREVIEW = NARRATION_SCALE < 1.0


def estimate_duration(text: str) -> float:
    clean = _BOOKMARK.sub("", text)
    words = len(clean.split())
    sentences = len(re.findall(r"[.!?]", clean))
    commas = len(re.findall(r"[,;—:]", clean))
    raw = words / WORDS_PER_SEC + sentences * SENTENCE_PAUSE + commas * COMMA_PAUSE
    return raw * NARRATION_SCALE


class _EstimatedTracker:
    """Står inn for VoiceoverTracker når vi rendrer uten lyd.

    Samme API (duration, get_remaining_duration, time_until_bookmark), slik at
    scenekoden er identisk med og uten ekte tale.
    """

    def __init__(self, scene: Scene, text: str):
        self.scene = scene
        self.duration = estimate_duration(text)
        self.start_t = float(scene.renderer.time or 0)
        self.end_t = self.start_t + self.duration

        content = ""
        self.bookmark_times = {}
        parts = re.split(r"(<bookmark\s*mark\s*=\s*['\"].*?['\"]\s*/>)", text)
        net_len = max(len(_BOOKMARK.sub("", text)), 1)
        for p in parts:
            m = _BOOKMARK.match(p)
            if m:
                frac = len(content) / net_len
                self.bookmark_times[m.group(1)] = self.start_t + frac * self.duration
            else:
                content += p

    def get_remaining_duration(self, buff: float = 0.0) -> float:
        return max(self.end_t - float(self.scene.renderer.time) + buff, 0.0)

    def time_until_bookmark(self, mark: str, buff: float = 0.0, limit=None) -> float:
        result = max(self.bookmark_times[mark] - float(self.scene.renderer.time) + buff, 0.0)
        return min(limit, result) if limit is not None else result


class NarrationMixin:
    """Gir scenen self.narrate(...) enten med ekte VO eller estimert timing."""

    def setup(self):
        super().setup()
        if USE_VOICE:
            self.set_speech_service(speech_service())

    def safe_wait(self, duration: float) -> None:
        if duration > 1 / config["frame_rate"]:
            self.wait(duration)

    def cue(self, tracker, frac: float) -> None:
        """Vent til vi er `frac` inn i replikken.

        Alternativet — å spille av alt med én gang og så la
        get_remaining_duration() spise resten — gjør at grafikken er ferdig
        etter sju sekunder og blir stående stille i ti. Med cue() kan hvert
        slag legges der setningen sin er, uten bookmarks."""
        elapsed = tracker.duration - tracker.get_remaining_duration()
        self.safe_wait(tracker.duration * frac - elapsed)

    @contextmanager
    def narrate(self, text: str):
        text = " ".join(text.split())
        if USE_VOICE:
            with self.voiceover(text=text) as tracker:
                yield tracker
        else:
            tracker = _EstimatedTracker(self, text)
            self._estimated_tracker = tracker
            try:
                yield tracker
            finally:
                self.safe_wait(tracker.get_remaining_duration())

    def beat(self, t: float = 0.4) -> None:
        self.safe_wait(t * NARRATION_SCALE)

    def clear_out(self, run_time: float = 0.8) -> None:
        """Toner ut alt — hver scene slutter i svart så klippene skjøtes rent."""
        mobs = [m for m in self.mobjects if m is not None]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)
        self.wait(0.25)


if USE_VOICE:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.elevenlabs import ElevenLabsService

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    if "ELEVEN_API_KEY" not in os.environ and "ELEVENLABS_API_KEY" in os.environ:
        os.environ["ELEVEN_API_KEY"] = os.environ["ELEVENLABS_API_KEY"]

    # ElevenLabs' standardbibliotek. manim-voiceover slår normalt opp stemmer via
    # API-et, men det krever `voices_read` på nøkkelen — vi går rett på id-en i stedet.
    VOICE_IDS = {
        "Adam": "pNInz6obpgDQGcFmaJgB",
        "Josh": "TxGEqnHWrfWFTfGW9XjX",
        "Antoni": "ErXwobaYiN019PkySvjV",
        "Arnold": "VR6AewLTigWG4xSOukaG",
        "Sam": "yoZ06aMxZJJ28mfd3POQ",
        "Rachel": "21m00Tcm4TlvDq8ikWAM",
        "Bella": "EXAVITQu4vr4xnSDxMaL",
        "Elli": "MF3mGyEYCl7XYWbV9V6O",
        "Domi": "AZnzlk1XvdvUeBnXmlld",
    }

    class DirectVoiceService(ElevenLabsService):
        """Som ElevenLabsService, men uten oppslag mot /voices."""

        def _select_voice(self, voice_name, voice_id):
            from elevenlabs import Voice

            vid = voice_id or VOICE_IDS.get(voice_name or "", "")
            if not vid:
                raise ValueError(
                    f"Ukjent stemme {voice_name!r}. Sett VOICE_ID direkte, "
                    f"eller velg en av: {', '.join(VOICE_IDS)}"
                )
            return Voice(voice_id=vid)

    def speech_service():
        return DirectVoiceService(
            voice_name=os.environ.get("VOICE_NAME", "Adam"),
            voice_id=os.environ.get("VOICE_ID") or None,
            model=os.environ.get("VOICE_MODEL", "eleven_multilingual_v2"),
            voice_settings={
                "stability": 0.45,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
            transcription_model=None,
        )

    class NarratedScene(NarrationMixin, VoiceoverScene):
        pass

    class Narrated3DScene(NarrationMixin, VoiceoverScene, ThreeDScene):
        pass

else:

    class NarratedScene(NarrationMixin, Scene):
        pass

    class Narrated3DScene(NarrationMixin, ThreeDScene):
        pass
