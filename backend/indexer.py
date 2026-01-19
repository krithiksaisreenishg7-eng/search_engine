import re
import math
from collections import defaultdict, Counter
from typing import List, Dict, Set
import string


class Indexer:
    """Indexer for building inverted index with TF-IDF scoring."""

    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'their', 'this', 'but', 'they',
            'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why',
            'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'or', 'than', 'too', 'very', 'can',
            'just', 'should', 'now'
        }

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Convert to lowercase
        text = text.lower()

        # Remove punctuation and split
        text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)

        # Split into words
        words = text.split()

        # Filter stop words and short words
        words = [w for w in words if w not in self.stop_words and len(w) > 2]

        return words

    def calculate_tf(self, terms: List[str]) -> Dict[str, float]:
        """Calculate term frequency for a list of terms."""
        term_count = Counter(terms)
        total_terms = len(terms)

        tf = {}
        for term, count in term_count.items():
            tf[term] = count / total_terms if total_terms > 0 else 0

        return tf

    def calculate_idf(self, term: str, total_docs: int,
                      docs_with_term: int) -> float:
        """Calculate inverse document frequency for a term."""
        if docs_with_term == 0:
            return 0

        return math.log((total_docs + 1) / (docs_with_term + 1)) + 1

    def build_index(self, pages: List[Dict]) -> Dict[str, Dict]:
        """Build inverted index with TF-IDF scores."""
        # First pass: count document frequency for each term
        df = defaultdict(int)
        page_terms = {}

        for page in pages:
            # Combine title and content with title weight
            text = f"{page['title']} {page['title']} {page['content']}"
            terms = self.tokenize(text)
            page_terms[page['url']] = terms

            # Count unique terms per document
            unique_terms = set(terms)
            for term in unique_terms:
                df[term] += 1

        total_docs = len(pages)

        # Second pass: calculate TF-IDF and build index
        inverted_index = defaultdict(list)

        for page in pages:
            terms = page_terms[page['url']]
            tf = self.calculate_tf(terms)

            # Calculate TF-IDF for each term
            for term, tf_value in tf.items():
                idf = self.calculate_idf(term, total_docs, df[term])
                tf_idf = tf_value * idf

                # Find positions of term in text
                positions = [i for i, t in enumerate(terms) if t == term]

                inverted_index[term].append({
                    'page': page,
                    'tf_idf': tf_idf,
                    'positions': positions
                })

        return dict(inverted_index)

    def get_term_positions(self, text: str, term: str) -> List[int]:
        """Get positions of a term in text."""
        terms = self.tokenize(text)
        return [i for i, t in enumerate(terms) if t == term]


class PageRankCalculator:
    """Calculate PageRank scores for pages."""

    def __init__(self, damping_factor: float = 0.85, iterations: int = 20):
        self.damping_factor = damping_factor
        self.iterations = iterations

    def calculate(self, pages: List[Dict], links: List[tuple]) -> Dict[int, float]:
        """
        Calculate PageRank scores.

        Args:
            pages: List of page dictionaries with 'id' key
            links: List of (from_page_id, to_page_id) tuples

        Returns:
            Dictionary mapping page_id to PageRank score
        """
        page_ids = [p['id'] for p in pages]
        n = len(page_ids)

        if n == 0:
            return {}

        # Initialize PageRank
        page_rank = {page_id: 1.0 / n for page_id in page_ids}

        # Build outgoing links map
        outgoing = defaultdict(list)
        for from_id, to_id in links:
            outgoing[from_id].append(to_id)

        # Iterate PageRank calculation
        for iteration in range(self.iterations):
            new_rank = {}

            for page_id in page_ids:
                # Calculate rank from incoming links
                rank_sum = 0.0

                for from_id, to_id in links:
                    if to_id == page_id:
                        # Add contribution from incoming link
                        num_outgoing = len(outgoing[from_id])
                        if num_outgoing > 0:
                            rank_sum += page_rank[from_id] / num_outgoing

                # Apply PageRank formula
                new_rank[page_id] = (1 - self.damping_factor) / n + \
                                    self.damping_factor * rank_sum

            page_rank = new_rank

        return page_rank
