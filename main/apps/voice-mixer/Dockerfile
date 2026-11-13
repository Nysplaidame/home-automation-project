# Voice Mixer image for CT 114 llm-host (CPU only).
#   docker build -t voice-mixer:local .                      # mixer + Piper
#   docker build -t voice-mixer:local --build-arg WITH_RVC=1 .   # + RVC on CPU (large image)
# VLAN 20 has no internet egress: build on a machine with internet and `docker save | docker load`.
FROM python:3.10-slim-bookworm

ARG WITH_RVC=0
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    GRADIO_ANALYTICS_ENABLED=False \
    HF_HUB_OFFLINE=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    VOICE_MIXER_CONFIG=/data/config.json \
    VOICE_MIXER_HOST=0.0.0.0 \
    VOICE_MIXER_PORT=7860

RUN apt-get update \
 && apt-get install -y --no-install-recommends libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements-rvc.txt ./
RUN pip install -r requirements.txt
RUN if [ "$WITH_RVC" = "1" ]; then \
      apt-get update && apt-get install -y --no-install-recommends build-essential git ffmpeg \
      && pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu \
      && pip install -r requirements-rvc.txt "numpy==1.23.5" \
      && apt-get purge -y build-essential git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/* \
      # rvc-python fetches hubert/rmvpe base models on first use; bake them in (runtime is offline)
      && python -c "import os, rvc_python; from rvc_python.download_model import download_rvc_models; download_rvc_models(os.path.dirname(rvc_python.__file__))" \
      && ls -la /usr/local/lib/python3.10/site-packages/rvc_python/base_model; \
    fi

COPY voicefx ./voicefx
COPY voice_mixer ./voice_mixer
COPY presets ./presets
COPY radio_fx.py ./
COPY packaging/config.container.json ./packaging/config.container.json

RUN useradd --uid 1000 --create-home mixer && mkdir -p /data && chown mixer:mixer /data \
 # rvc-python rewrites its own config JSONs and modules/train/preprocess.py on every CPU start,
 # so the mixer user must own that one package (nothing else in site-packages)
 && if [ -d /usr/local/lib/python3.10/site-packages/rvc_python ]; then \
      chown -R mixer:mixer /usr/local/lib/python3.10/site-packages/rvc_python; fi
USER mixer
VOLUME ["/data"]
EXPOSE 7860
HEALTHCHECK --interval=60s --timeout=5s --start-period=60s \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:7860/',timeout=4)" || exit 1
# First start copies the container config (container paths) into /data unless one exists.
CMD ["sh", "-c", "[ -f /data/config.json ] || cp /app/packaging/config.container.json /data/config.json; exec python voice_mixer/__main__.py"]
