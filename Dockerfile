# ── Stage 1: Build the React frontend ──────────────────────────────────
FROM node:22-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python backend + serve built frontend ────────────────────
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend into backend/static
COPY --from=frontend-build /frontend/dist ./static

# Railway sets PORT env var; default to 8000
ENV PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
