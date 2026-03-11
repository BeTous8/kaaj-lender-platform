# Kaaj Lender Platform

## Demo & Walkthrough

🎬 **[Watch the Demo & Code Walkthrough on Loom](https://www.loom.com/share/5c3494b8afea4761b48e3eb270c54b8f)**

Equipment finance loan broker platform. Brokers submit applications; the system matches them against lender credit policies and returns approve/decline decisions with explanations.

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ running on port 5433

## Backend

```bash
cd backend
cp .env.example .env        # edit DATABASE_URL if needed
pip install -r requirements.txt
alembic upgrade head        # create tables
python seed.py              # seed 5 lenders with programs and rules
uvicorn main:app --reload   # start API server
```

API runs at http://localhost:8000
Swagger docs at http://localhost:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at http://localhost:5173

## Usage

1. Open http://localhost:5173
2. Fill out the **New Application** form and click Submit
3. The system underwrites the application and shows match results
4. Use the **Policies** page to view and edit lender rules
