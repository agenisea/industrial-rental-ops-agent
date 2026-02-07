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
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./static/

# Create logs directory
RUN mkdir -p logs

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "ops_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
