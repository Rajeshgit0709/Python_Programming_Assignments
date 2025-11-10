from __future__ import annotations

from pathlib import Path

from usecases.load_csv_to_mariadb import load_csv_to_mariadb
from usecases.search_mongodb import search_text
from usecases.transfer_mariadb_to_mongodb import transfer_mariadb_to_mongodb

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "data" / "articles.csv"
PAPERS_DIR = ROOT / "papers"

def main() -> None:
    print("1) Loading CSV into MariaDB...")
    a_count, art_count = load_csv_to_mariadb(CSV_PATH)
    print(f"   OK: {a_count} authors, {art_count} articles.")

    print("2) Transferring from MariaDB to MongoDB (with PDF->Markdown)...")
    inserted = transfer_mariadb_to_mongodb(PAPERS_DIR)
    print(f"   Inserted {inserted} docs into MongoDB.")

    print("3) Sample search on MongoDB text index...")
    results = search_text("Transformer OR Residual")
    for title, score in results:
        print(f"   - {title} (score={score:.3f})")

if __name__ == "__main__":
    main()
