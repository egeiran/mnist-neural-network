PY = .venv/bin/python
MANIM = .venv/bin/manim

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

# Én scene, rask forhåndsvisning:  make scene S=s04_sigmoid C=S04Sigmoid
scene:
	PYTHONPATH=. $(MANIM) -pql scenes/$(S).py $(C)

hq:
	PYTHONPATH=. $(MANIM) -pqh scenes/$(S).py $(C)

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

.PHONY: train train-live test artifacts scene hq video video-preview video-hq video-vo clean
