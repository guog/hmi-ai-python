FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1

COPY ./ /hmi-ai-python
WORKDIR /hmi-ai-python/

# Install system dependencies
RUN apt-get update && apt-get install -y \
  ffmpeg \
  libsm6 \
  libxext6

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.7.5 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/hmi-ai-python/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project

ENV PYTHONPATH=/hmi-ai-python

# PaddleOCR的模型存储路径
ENV PADDLE_OCR_BASE_DIR=/hmi-ai-python/models/paddleocr


# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync


CMD ["fastapi", "run", "--workers", "4", "app/main.py"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=5 CMD [ "curl", "-f", "http://localhost:8000/utils/health-check/" ]
