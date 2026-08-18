#!/usr/bin/env bash
# Rendrer alle scenene i rekkefølge og skjøter dem til én film.
#
#   ./build.sh              720p30 (standard)
#   QUALITY=h ./build.sh    1080p60
#   QUALITY=l ./build.sh    480p15 (rask forhåndsvisning)
#   VOICEOVER=1 ./build.sh  med ElevenLabs-tale (bruker API-kreditter)
set -euo pipefail

cd "$(dirname "$0")"

QUALITY="${QUALITY:-m}"
case "$QUALITY" in
  l) RES="480p15" ;;
  m) RES="720p30" ;;
  h) RES="1080p60" ;;
  k) RES="2160p60" ;;
  *) echo "ukjent QUALITY=$QUALITY (bruk l, m, h eller k)"; exit 1 ;;
esac

MANIM=".venv/bin/manim"
OUT_DIR="artifacts"
OUT="$OUT_DIR/neural-network-$RES.mp4"

SCENES=(
  "s01_problem:S01Problem"
  "s02_image_to_vector:S02ImageToVector"
  "s03_one_neuron:S03OneNeuron"
  "s04_sigmoid:S04Sigmoid"
  "s05_layers_matrices:S05LayersMatrices"
  "s06_forward_loss:S06ForwardLoss"
  "s07_gradient_descent:S07GradientDescent"
  "s08_backprop:S08Backprop"
  "s09_grad_check:S09GradCheck"
  "s10_training:S10Training"
  "s11_what_it_learned:S11WhatItLearned"
)

if [ ! -f artifacts/run.npz ]; then
  echo "artifacts/run.npz mangler — trener nettverket først"
  .venv/bin/python -m nn.artifacts
fi

# Med voiceover: generer all lyd først (med retry), så rendringen bare leser cache
if [ "${VOICEOVER:-0}" != "0" ]; then
  .venv/bin/python prepare_vo.py
fi

# FAST/SPEED hører til forhåndsvisning — sniker de seg inn her blir filmen
# kortet ned uten at man ser det før etterpå.
if [ "${FAST:-0}" != "0" ] || [ -n "${SPEED:-}" ]; then
  echo "advarsel: FAST/SPEED er satt — narrasjonen kortes ned i denne filmen"
fi

LIST="$(mktemp)"
trap 'rm -f "$LIST"' EXIT

for entry in "${SCENES[@]}"; do
  file="${entry%%:*}"
  klass="${entry##*:}"
  echo "── rendrer $klass ($RES)"
  # --disable_caching: hashingen koster mer enn cachen sparer her.
  # --max-inflight-encoders: ffmpeg encoder mens neste animasjon tegnes.
  PYTHONPATH=. "$MANIM" --config_file render.cfg -q"$QUALITY" \
    --disable_caching --max-inflight-encoders 4 \
    "scenes/$file.py" "$klass" >/dev/null
  mp4="media/videos/$file/$RES/$klass.mp4"
  [ -f "$mp4" ] || { echo "fant ikke $mp4"; exit 1; }
  echo "file '$PWD/$mp4'" >> "$LIST"
  # LEAN=1: kast mellomfilene med én gang (sparer disk, koster full rerender senere)
  if [ "${LEAN:-0}" != "0" ]; then
    rm -rf "media/videos/$file/$RES/partial_movie_files"
  fi
done

mkdir -p "$OUT_DIR"
echo "── skjøter sammen → $OUT"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy "$OUT"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
awk -v d="$DUR" -v f="$OUT" 'BEGIN { printf "ferdig: %s  (%.0f sek = %d:%02d)\n", f, d, int(d/60), int(d)%60 }' 
