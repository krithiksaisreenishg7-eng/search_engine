from typing import List, Dict
from collections import defaultdict
from backend.database import Database
from backend.indexer import Indexer
import math


class SearchEngine:
    """Search engine with ranking capabilities."""

    def __init__(self, database: Database):
        self.db = database
        self.indexer = Indexer()

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for pages matching the query.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of search results with scores
        """
        # Tokenize query
        query_terms = self.indexer.tokenize(query)

        if not query_terms:
            return []

        # Search index for each term
        results = self.db.search_index(query_terms)

        if not results:
            return []

        # Group results by page
        page_scores = defaultdict(lambda: {
            'url': '',
            'title': '',
            'content': '',
            'meta_description': '',
            'page_rank': 1.0,
            'tf_idf_score': 0.0,
            'term_matches': 0
        })

        for result in results:
            page_id = result['id']

            if not page_scores[page_id]['url']:
                page_scores[page_id]['url'] = result['url']
                page_scores[page_id]['title'] = result['title']
                page_scores[page_id]['content'] = result['content']
                page_scores[page_id]['meta_description'] = result['meta_description']
                page_scores[page_id]['page_rank'] = result['page_rank']

            # Accumulate TF-IDF scores
            page_scores[page_id]['tf_idf_score'] += result['tf_idf']
            page_scores[page_id]['term_matches'] += 1

        # Calculate final scores
        ranked_results = []

        for page_id, data in page_scores.items():
            # Combine TF-IDF score with PageRank
            # Weight TF-IDF more heavily than PageRank
            final_score = (data['tf_idf_score'] * 0.7 +
                          data['page_rank'] * 0.3)

            # Boost score based on number of matching terms
            term_match_boost = data['term_matches'] / len(query_terms)
            final_score *= (1 + term_match_boost)

            # Create snippet
            snippet = self.create_snippet(
                data['content'],
                query_terms,
                max_length=200
            )

            ranked_results.append({
                'url': data['url'],
                'title': data['title'],
                'snippet': snippet,
                'meta_description': data['meta_description'],
                'score': final_score,
                'page_rank': data['page_rank']
            })

        # Sort by score (descending)
        ranked_results.sort(key=lambda x: x['score'], reverse=True)

        return ranked_results[:limit]

    def create_snippet(self, content: str, query_terms: List[str],
                      max_length: int = 200) -> str:
        """
        Create a snippet highlighting query terms.

        Args:
            content: Full page content
            query_terms: List of search terms
            max_length: Maximum snippet length

        Returns:
            Snippet with highlighted terms
        """
        if not content:
            return ""

        # Tokenize content
        content_lower = content.lower()
        words = content.split()

        # Find first occurrence of any query term
        best_position = 0
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:')
            if any(term in word_lower for term in query_terms):
                best_position = max(0, i - 10)
                break

        # Extract snippet around the position
        snippet_words = words[best_position:best_position + 30]
        snippet = ' '.join(snippet_words)

        # Truncate to max length
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + '...'
        elif best_position > 0:
            snippet = '...' + snippet

        return snippet

    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on indexed terms.

        Args:
            query: Partial query string
            limit: Maximum number of suggestions

        Returns:
            List of suggested queries
        """
        if not query:
            return []

        query_lower = query.lower()
        suggestions = []

        # Get all pages and extract common terms
        pages = self.db.get_all_pages()
        all_terms = set()

        for page in pages:
            text = f"{page['title']} {page['content']}"
            terms = self.indexer.tokenize(text)
            all_terms.update(terms)

        # Find terms that start with query
        matching_terms = [
            term for term in all_terms
            if term.startswith(query_lower)
        ]

        # Sort by length (prefer shorter terms) and take top N
        matching_terms.sort(key=len)

        return matching_terms[:limit]

    def index_pages(self, pages: List[Dict]):
        """
        Index a list of pages.

        Args:
            pages: List of page dictionaries
        """
        print(f"Indexing {len(pages)} pages...")

        # Build inverted index
        inverted_index = self.indexer.build_index(pages)

        # Clear existing index
        self.db.clear_index()

        # Store pages and index in database
        for page in pages:
            # Add page to database
            page_id = self.db.add_page(
                url=page['url'],
                title=page['title'],
                content=page['content'],
                meta_description=page.get('meta_description', '')
            )

            if not page_id:
                continue

            # Add links
            for link_url in page.get('links', []):
                self.db.add_link(page['url'], link_url)

        # Add terms to inverted index
        for term, postings in inverted_index.items():
            for posting in postings:
                page_url = posting['page']['url']
                page = self.db.get_page_by_url(page_url)

                if page:
                    self.db.add_to_index(
                        term=term,
                        page_id=page['id'],
                        tf_idf=posting['tf_idf'],
                        positions=posting['positions']
                    )

        print(f"Indexed {len(pages)} pages with {len(inverted_index)} unique terms")

    def get_stats(self) -> Dict:
        """Get search engine statistics."""
        pages = self.db.get_all_pages()

        return {
            'total_pages': len(pages),
            'total_links': len(self.db.get_links())
        }
