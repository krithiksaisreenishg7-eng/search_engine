import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


class Database:
    """Database handler for the search engine."""

    def __init__(self, db_path: str = "search_engine.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize the database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table for indexed web pages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content TEXT,
                meta_description TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                page_rank REAL DEFAULT 1.0
            )
        ''')

        # Table for inverted index
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inverted_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL,
                page_id INTEGER NOT NULL,
                tf_idf REAL,
                positions TEXT,
                FOREIGN KEY (page_id) REFERENCES pages(id),
                UNIQUE(term, page_id)
            )
        ''')

        # Index for faster search
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_term
            ON inverted_index(term)
        ''')

        # Table for links between pages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_page_id INTEGER NOT NULL,
                to_page_id INTEGER NOT NULL,
                FOREIGN KEY (from_page_id) REFERENCES pages(id),
                FOREIGN KEY (to_page_id) REFERENCES pages(id),
                UNIQUE(from_page_id, to_page_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_page(self, url: str, title: str, content: str,
                 meta_description: str = "") -> Optional[int]:
        """Add or update a page in the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO pages (url, title, content, meta_description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content,
                    meta_description = excluded.meta_description,
                    indexed_at = CURRENT_TIMESTAMP
            ''', (url, title, content, meta_description))

            # Get the page ID
            cursor.execute('SELECT id FROM pages WHERE url = ?', (url,))
            page_id = cursor.fetchone()[0]

            conn.commit()
            return page_id
        except Exception as e:
            print(f"Error adding page: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def add_to_index(self, term: str, page_id: int, tf_idf: float,
                     positions: List[int]):
        """Add a term to the inverted index."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO inverted_index (term, page_id, tf_idf, positions)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(term, page_id) DO UPDATE SET
                    tf_idf = excluded.tf_idf,
                    positions = excluded.positions
            ''', (term, page_id, tf_idf, json.dumps(positions)))

            conn.commit()
        except Exception as e:
            print(f"Error adding to index: {e}")
            conn.rollback()
        finally:
            conn.close()

    def search_index(self, terms: List[str]) -> List[Dict[str, Any]]:
        """Search the inverted index for given terms."""
        conn = self.get_connection()
        cursor = conn.cursor()

        placeholders = ','.join(['?' for _ in terms])
        query = f'''
            SELECT
                p.id,
                p.url,
                p.title,
                p.content,
                p.meta_description,
                p.page_rank,
                i.term,
                i.tf_idf
            FROM inverted_index i
            JOIN pages p ON i.page_id = p.id
            WHERE i.term IN ({placeholders})
        '''

        cursor.execute(query, terms)
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]

    def get_page_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get a page by URL."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pages WHERE url = ?', (url,))
        result = cursor.fetchone()
        conn.close()

        return dict(result) if result else None

    def get_all_pages(self) -> List[Dict[str, Any]]:
        """Get all indexed pages."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM pages')
        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]

    def add_link(self, from_url: str, to_url: str):
        """Add a link between two pages."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get page IDs
            cursor.execute('SELECT id FROM pages WHERE url = ?', (from_url,))
            from_page = cursor.fetchone()
            cursor.execute('SELECT id FROM pages WHERE url = ?', (to_url,))
            to_page = cursor.fetchone()

            if from_page and to_page:
                cursor.execute('''
                    INSERT OR IGNORE INTO links (from_page_id, to_page_id)
                    VALUES (?, ?)
                ''', (from_page[0], to_page[0]))

                conn.commit()
        except Exception as e:
            print(f"Error adding link: {e}")
            conn.rollback()
        finally:
            conn.close()

    def update_page_rank(self, page_id: int, page_rank: float):
        """Update the PageRank score for a page."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE pages SET page_rank = ? WHERE id = ?
        ''', (page_rank, page_id))

        conn.commit()
        conn.close()

    def get_links(self) -> List[tuple]:
        """Get all links for PageRank calculation."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT from_page_id, to_page_id FROM links
        ''')
        results = cursor.fetchall()
        conn.close()

        return [(row[0], row[1]) for row in results]

    def clear_index(self):
        """Clear the inverted index."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM inverted_index')
        conn.commit()
        conn.close()
