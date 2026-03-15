# Stage 1: Build React frontend
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

# Stage 2: Python backend + serve static files
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY backend/src/ ./src/
COPY backend/data/ ./data/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./static/

# Create non-root user with home directory for uv cache
RUN useradd -r -m -s /usr/sbin/nologin app && mkdir -p logs && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "ops_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
