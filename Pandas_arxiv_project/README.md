# Enhancing the Data Pipeline with Pandas and ArXiv API

## What this does
- Uses **pandas DataFrame** as the primary data structure (string dtype).
- Fetches articles from the **ArXiv API**, parses **XML**, and normalizes into the same schema as your CSV.
- Downloads each article's **HTML** page and adds it to the DataFrame with `.apply()`.
- Loads to **MariaDB** using `.apply()` and appends returned **author_id/article_id** back into the DataFrame.
- Loads to **MongoDB** using **HTML→text** (no PDFs) and stores an **embedding** for future similarity work.
- Adds a **text index** and demonstrates a search query.

## Run it
1. Start databases (MariaDB + MongoDB):
	```bash
	docker compose up -d
	```
2. Copy environment defaults and adjust if required:
	```bash
	cp .env.example .env
	```
3. Create / activate a virtual environment and install the project:
	```bash
	python -m venv .venv
	# PowerShell
	.\.venv\Scripts\Activate.ps1
	pip install -e .
	```
4. Seed from CSV and run the ArXiv pipeline:
	```bash
	python main.py --csv data/articles.csv --query "transformer" --max-results 5
	```
	Use `--skip-csv` if you only want to fetch from ArXiv, or `--search "term"` to test a custom query.

## Lint / Type check
```bash
ruff check .
mypy .
```
