# FairLens

A full-stack platform to measure, flag, and fix hidden bias in datasets and ML models.

## Status: In active development (Phase 3 complete)

## Architecture
- **Backend**: FastAPI + Fairlearn (bias detection engine)
- **Frontend**: React (planned)
- **LLM layer**: Gemini 2.5 Flash — evidence-constrained report generation only; never computes metrics
