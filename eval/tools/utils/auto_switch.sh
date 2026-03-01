#!/usr/bin/env bash

_SROOT="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"

$_SROOT/current/llama-server \
  --models-max 1 \
  --models-preset $_SROOT/presets/mypresets.ini \
	--host 0.0.0.0 --port 8400  \
	--no-warmup \
	-fa on --jinja --reasoning-format auto

	# --no-mmap \
  #dd--mlock -np 4 -kvu \
	# -cmoe \ crash
	# -c 40960 \
	# -b 1024 -ub 1024 \
	# -n -2 \
