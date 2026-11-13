# Derived from obico-server release/ml_api/Dockerfile.
# The Automation VLAN permits only TLS WAN egress during an explicitly approved
# build, so Ubuntu package sources are upgraded from HTTP to HTTPS here.
ARG IMAGE_TAG_SUFFIX=
FROM thespaghettidetective/ml_api_base:1.4${IMAGE_TAG_SUFFIX}

RUN sed -i \
      -e 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g' \
      -e 's|http://security.ubuntu.com|https://security.ubuntu.com|g' \
      /etc/apt/sources.list \
 && apt update \
 && apt install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
EXPOSE 3333

ADD . /app
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /model_cache/ml_api/darknet /model_cache/ml_api/onnx /model_cache/ml_api/rknn \
 && echo 'Downloading the latest failure detection AI model in Darknet format...' \
 && curl -fsSL -o /model_cache/ml_api/darknet/model-weights.darknet "$(tr -d '\r' < model/model-weights.darknet.url)" \
 && echo 'Downloading the latest failure detection AI model in ONNX format...' \
 && curl -fsSL -o /model_cache/ml_api/onnx/model-weights.onnx "$(tr -d '\r' < model/model-weights.onnx.url)" \
 && echo 'Downloading the latest failure detection AI model in RKNN format...' \
 && curl -fsSL -o /model_cache/ml_api/rknn/model-weights.rknn "$(tr -d '\r' < model/model-weights.rknn.url)"
