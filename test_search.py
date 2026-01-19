#!/usr/bin/env python3
"""Quick test script for the search engine."""

from backend.database import Database
from backend.search_engine import SearchEngine
from backend.crawler import get_sample_data
from backend.indexer import PageRankCalculator


def test_search_engine():
    """Test the search engine functionality."""
    print("Testing Search Engine...")
    print("=" * 50)

    # Initialize
    db = Database("test_search_engine.db")
    search_engine = SearchEngine(db)

    # Get sample data
    print("\n1. Loading sample data...")
    pages = get_sample_data()
    print(f"   ✓ Loaded {len(pages)} sample pages")

    # Index pages
    print("\n2. Indexing pages...")
    search_engine.index_pages(pages)
    print("   ✓ Pages indexed successfully")

    # Calculate PageRank
    print("\n3. Calculating PageRank...")
    all_pages = db.get_all_pages()
    links = db.get_links()
    pr_calculator = PageRankCalculator()
    page_ranks = pr_calculator.calculate(all_pages, links)
    for page_id, score in page_ranks.items():
        db.update_page_rank(page_id, score)
    print("   ✓ PageRank calculated")

    # Test searches
    print("\n4. Testing search queries...")
    test_queries = [
        "python",
        "javascript",
        "web development",
        "machine learning",
        "api",
    ]

    for query in test_queries:
        results = search_engine.search(query, limit=3)
        print(f"\n   Query: '{query}'")
        print(f"   Results: {len(results)}")
        if results:
            for i, result in enumerate(results[:2], 1):
                print(f"      {i}. {result['title'][:50]}... (score: {result['score']:.2f})")

    # Get statistics
    print("\n5. Statistics:")
    stats = search_engine.get_stats()
    print(f"   Total pages: {stats['total_pages']}")
    print(f"   Total links: {stats['total_links']}")

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("\nSearch engine is ready to use!")
    print("Run 'python main.py' to start the web server")


if __name__ == "__main__":
    test_search_engine()
