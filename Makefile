PY = .venv/bin/python
MANIM = .venv/bin/manim

train:
	$(PY) -m nn.train

test:
	$(PY) -m nn.network

scene:
	PYTHONPATH=. $(MANIM) -pql scenes/$(S).py $(C)

hq:
	PYTHONPATH=. $(MANIM) -pqh scenes/$(S).py $(C)

clean:
	rm -rf media/videos media/images
	find . -name __pycache__ -type d -exec rm -rf {} +