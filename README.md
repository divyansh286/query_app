# Query Transformer

Small Python app that takes a query, stores it in SQLite, applies a transformation, and shows a simple web UI.

## Run

1. Create a virtual environment (optional) and install deps:

   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt

2. Start the app:

   python app.py

3. Open http://127.0.0.1:5000

## Notes
- Database: `data.db` (SQLite)
- The app is tiny and will be well under 500 MB.
