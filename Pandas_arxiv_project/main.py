from __future__ import annotations
from usecases.pandas_pipeline import run_arxiv_pipeline
from usecases.search_mongodb import search_text

def main() -> None:
    print("=== API-driven pipeline (pandas + ArXiv) ===")
    result = run_arxiv_pipeline("transformer OR residual OR BERT", max_results=10)
    print(f"Inserted into MongoDB: {result.inserted_mongo}")
    print("DataFrame ID columns:", [c for c in result.df.columns if c.endswith("_id")])

    print("\n=== Verify search (MongoDB text index) ===")
    for title, score in search_text("Transformer OR Residual OR BERT"):
        print(f"- {title} (score={score:.3f})")

if __name__ == "__main__":
    main()
