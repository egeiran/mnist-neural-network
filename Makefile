PY = .venv/bin/python
MANIM = .venv/bin/manim

# N=3,6 → bare animasjon 3 til 6.  FAST/SPEED leses av scenes/common.py.
NFLAG = $(if $(N),-n $(N),)

# Dropper du C=, rendres alle scenene i fila (-a). Hver fil her har én, så i
# praksis betyr det bare at du slipper å skrive klassenavnet.
ALLFLAG = $(if $(C),,-a)

# Manims cache koster mer å regne ut (den hasher hele mobject-treet) enn den
# sparer — målt på s02/s04 er en cache-treff-rerender tregere enn å bare rendre
# på nytt uten. Parallelle encodere lar ffmpeg jobbe mens neste animasjon
# tegnes. Til sammen ~30 % raskere. TURBO= slår det av igjen.
TURBO = --disable_caching --max-inflight-encoders 4
export FAST
export SPEED

train:
	$(PY) -m nn.train

# Samme, men med et vindu som viser vektene bli til underveis
train-live:
	LIVE=1 $(PY) -m nn.train

test:
	$(PY) -m nn.network

# Trener og lagrer alle tallene scenene viser (artifacts/run.npz)
artifacts:
	$(PY) -m nn.artifacts

# Én scene, rask forhåndsvisning:  make scene S=s04_sigmoid
# Klassenavnet kan utelates — da tas alt som ligger i fila.
# N=3,6 rendrer bare animasjon 3 til 6.  FAST=1 korter ned all ventetid.
scene:
	PYTHONPATH=. $(MANIM) -pql $(TURBO) $(ALLFLAG) $(NFLAG) scenes/$(S).py $(C)

hq:
	PYTHONPATH=. $(MANIM) -pqh $(TURBO) $(ALLFLAG) scenes/$(S).py $(C)

# --- Forhåndsvisning ---------------------------------------------------------
# Live OpenGL-vindu, ingen fil skrives, ingen venting på ffmpeg. Panorer med
# musa, zoom med scroll, lukk vinduet (eller ctrl-c) når du er ferdig.
#   make preview S=s04_sigmoid
#   make preview S=s04_sigmoid FAST=0   (ekte timing)
preview:
	PYTHONPATH=. FAST=$${FAST:-1} $(MANIM) --renderer=opengl -p $(ALLFLAG) $(NFLAG) scenes/$(S).py $(C)

# Bare ett bilde som PNG — raskeste måten å sjekke komposisjon og plassering på.
#   make still S=s04_sigmoid          (siste bilde i scenen)
#   make still S=s04_sigmoid N=0,12   (bildet etter animasjon 12)
still:
	PYTHONPATH=. FAST=$${FAST:-1} $(MANIM) -spql $(TURBO) $(ALLFLAG) $(NFLAG) scenes/$(S).py $(C)

# Rendrer på nytt hver gang du lagrer. Stillbilde som standard, V=1 gir video.
#   make watch S=s04_sigmoid
watch:
	$(PY) tools/watch.py "PYTHONPATH=. FAST=$${FAST:-1} $(MANIM) $(if $(V),-pql,-spql) $(TURBO) $(ALLFLAG) $(NFLAG) scenes/$(S).py $(C)"

# Interaktiv lekegrind: levende vindu + IPython-skall. Se scenes/sandbox.py.
play:
	PYTHONPATH=. $(MANIM) --renderer=opengl -p scenes/sandbox.py Sandbox

# Hele filmen
video:
	./build.sh

video-preview:
	QUALITY=l ./build.sh

video-hq:
	QUALITY=h ./build.sh

# Hele filmen med ElevenLabs-voiceover (bruker API-kreditter)
video-vo:
	VOICEOVER=1 ./build.sh

clean:
	rm -rf media/videos media/images
	find . -name __pycache__ -type d -exec rm -rf {} +

.PHONY: train train-live test artifacts scene hq preview still watch play video video-preview video-hq video-vo clean
