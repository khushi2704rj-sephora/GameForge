# Antigravity: The Game Theory Lab

A modern, interactive game theory simulation platform built with FastAPI, React, and D3/Plotly.

## Features
- **22 Interactive Simulations**: From Prisoner's Dilemma to Multi-Agent Negotiation.
- **Real-time Metrics**: Cooperation rates, Pareto optimality, Nash equilibrium detection.
- **Google-Inspired UI**: Material Design 3 aesthetics with motion curves and glassmorphism.
- **High Performance**: 100,000+ rounds/second backend computation.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, NumPy, SciPy (Optimization & Nashpy)
- **Frontend**: React 19, TypeScript, Vite, Plotly.js, Framer Motion (CSS)
- **Deployment**: Docker (Multi-stage build), Nginx, Railway/Render

## Local Development

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment
This project is configured for **Railway** deployment via GitHub Actions.
Pushing to the `main` branch automatically triggers a build and deploy.
