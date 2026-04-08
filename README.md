# NYC Restaurant Search

Vector-based restaurant retrieval project for NYC using PostgreSQL + pgvector.

The app supports two search modes:
- Natural language search (example: "great pizza with outdoor seating")
- Similar-restaurant search based on an existing restaurant

## Project Structure

```
src/
	database.py       # DB model + pgvector table setup
	process_data.py   # CSV ingest + embedding generation
	main.py           # FastAPI backend
	app.py            # Streamlit frontend
```

## Prerequisites

- Python 3.10+
- Docker (for PostgreSQL + pgvector)
- `pip`

## 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure Environment

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL="postgresql+psycopg://myuser:mypassword@localhost:5432/vectordb"
```

Notes:
- This project currently uses the local embedding model `all-MiniLM-L6-v2`.
- `OPENAI_API_KEY` is not required for the current implementation.

## 3. Start PostgreSQL with pgvector

```bash
docker compose up -d
```

This starts a Postgres instance on `localhost:5432`.

## 4. Process Data and Build Embeddings

Run once to create tables and ingest the CSV dataset:

```bash
python -m src.process_data
```

## 5. Launch the Backend API

In one terminal:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## 6. Launch the Streamlit App

In a second terminal (with the same virtual environment active):

```bash
streamlit run src/app.py
```

Open the app at:
- `http://localhost:8501`

## How to Use the App

1. Choose a mode:
	 - `Natural Language Search`
	 - `Find Similar Restaurants`
2. Set filters in the sidebar:
	 - Online ordering only
	 - Minimum reviews
	 - Number of results
3. Click `Search`.

## Troubleshooting

- If the frontend cannot connect to API:
	- Make sure FastAPI is running on `localhost:8000`.
- If search returns no records:
	- Make sure data ingest completed successfully via `python -m src.process_data`.
- If DB connection fails:
	- Verify `.env` `DATABASE_URL` and confirm Docker container is running.
