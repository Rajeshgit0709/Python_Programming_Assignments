# Data Processing Integration Pipeline

A complete, linted, and typed example that:
1. Loads `data/articles.csv` into **MariaDB** (via SQLAlchemy).
2. Transfers rows into **MongoDB** (via MongoEngine), converting each PDF in `papers/` into Markdown.
3. Creates a **text index** on the MongoDB `text` field and runs a sample **full‑text search**.

## Project Structure

```text
.
├── data/
│   └── articles.csv
├── papers/
│   ├── attention.pdf
│   ├── bert.pdf
│   └── resnet.pdf
├── models/
│   ├── mongo_models.py
│   └── sql_models.py
├── storage/
│   ├── mariadb.py
│   └── mongodb.py
├── usecases/
│   ├── load_csv_to_mariadb.py
│   ├── search_mongodb.py
│   └── transfer_mariadb_to_mongodb.py
├── main.py
├── pyproject.toml
├── docker-compose.yml
└── .env.example
```

## Quick Start

### 1) Bring up databases
```bash
docker compose up -d
```

### 2) Create `.env`
```bash
cp .env.example .env
# adjust if needed
```

### 3) Install deps
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 4) Lint & type-check
```bash
ruff check .
mypy .
```

### 5) Run the pipeline
```bash
python main.py
```

You should see:
- CSV rows loaded to MariaDB
- Documents inserted into MongoDB with `text` containing PDF->Markdown
- A sample search listing titles with text scores

## Notes

- Replace the sample PDFs with real arXiv PDFs if desired—just keep `file_path` in `articles.csv` consistent.
- The MongoDB text index is declared in `models/mongo_models.py` (`meta.indexes` with `$text` on `text`).
- The PDF-to-Markdown step uses `pypdf` for text extraction; if a PDF has no extractable text, a fallback string is used.
