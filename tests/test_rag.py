from pathlib import Path

from app.retrieval.service import RAGService


KNOWLEDGE_DIR = Path("knowledge")

DATABASE = Path("app/vectorstore/retrieval.db")


def main() -> None:

    rag = RAGService(
        knowledge_dir=KNOWLEDGE_DIR,
        db_path=DATABASE,
    )

    rag.initialize()

    results = rag.retrieve(
        "What is LangGraph?"
    )

    print()

    print("=" * 80)

    print("Search Results")

    print("=" * 80)

    for result in results:

        print()

        print(f"Score : {result.score:.4f}")

        print(f"Source: {result.chunk.source}")

        print()

        print(result.chunk.text[:300])

        print("-" * 80)


if __name__ == "__main__":
    main()