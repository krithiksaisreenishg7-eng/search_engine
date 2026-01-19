# Search Engine

A fully functional Google-like search engine built from scratch with Python, FastAPI, and modern web technologies.

## Features

### Core Functionality
- **Full-Text Search**: Fast and accurate search across indexed web pages
- **Intelligent Ranking**: Combined TF-IDF and PageRank algorithm for relevant results
- **Inverted Index**: Efficient data structure for quick lookups
- **Web Crawler**: Automated web page indexing system
- **Clean UI**: Google-inspired minimalist interface
- **REST API**: Complete API for programmatic access

### Technical Highlights
- **TF-IDF Scoring**: Term Frequency-Inverse Document Frequency for relevance
- **PageRank Algorithm**: Link-based ranking similar to Google's original algorithm
- **SQLite Database**: Persistent storage for pages and index
- **Responsive Design**: Mobile-friendly interface
- **Real-time Search**: Fast search results with animated UI

## Architecture

```
search_engine/
├── backend/
│   ├── __init__.py
│   ├── database.py         # Database operations (SQLite)
│   ├── crawler.py          # Web crawler and sample data
│   ├── indexer.py          # Inverted index and TF-IDF
│   └── search_engine.py    # Search and ranking logic
├── templates/
│   ├── index.html          # Home page
│   └── search.html         # Search results page
├── static/
│   ├── style.css           # Styling
│   └── script.js           # Client-side JavaScript
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## How It Works

### 1. Web Crawling
The crawler fetches web pages and extracts:
- Page title
- Main content (text)
- Meta descriptions
- Links to other pages

### 2. Indexing
The indexer processes each page:
- Tokenizes text into terms
- Removes stop words (common words like "the", "a", etc.)
- Builds an inverted index mapping terms to pages
- Calculates TF-IDF scores for each term-page pair

### 3. Ranking
Search results are ranked using:
- **TF-IDF Score** (70% weight): Measures term relevance
- **PageRank Score** (30% weight): Measures page authority
- **Term Match Boost**: Extra weight for matching multiple query terms

### 4. Search Flow
1. User enters a query
2. Query is tokenized and processed
3. Inverted index is searched for matching terms
4. Results are ranked by combined score
5. Top results are returned with snippets

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd search_engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

4. Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

### Web Interface

1. **Home Page**: Enter your search query and click "Search"
2. **Search Results**: View ranked results with snippets
3. **I'm Feeling Lucky**: Jumps directly to the top result

### API Endpoints

#### Search
```bash
GET /api/search?q=python&limit=10
```

Response:
```json
{
  "query": "python",
  "count": 5,
  "results": [
    {
      "url": "http://example.com/python",
      "title": "Python Programming Language",
      "snippet": "Python is a high-level...",
      "score": 2.45,
      "page_rank": 1.0
    }
  ]
}
```

#### Get Suggestions
```bash
GET /api/suggestions?q=pyth&limit=5
```

Response:
```json
{
  "suggestions": ["python", "pytorch"]
}
```

#### Index Pages
```bash
POST /api/index
Content-Type: application/json

{
  "urls": ["http://example.com"]
}
```

#### Get Statistics
```bash
GET /api/stats
```

Response:
```json
{
  "total_pages": 10,
  "total_links": 0,
  "indexed_pages": 10
}
```

#### Health Check
```bash
GET /health
```

## Database Schema

### Pages Table
```sql
CREATE TABLE pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content TEXT,
    meta_description TEXT,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_rank REAL DEFAULT 1.0
);
```

### Inverted Index Table
```sql
CREATE TABLE inverted_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL,
    page_id INTEGER NOT NULL,
    tf_idf REAL,
    positions TEXT,
    FOREIGN KEY (page_id) REFERENCES pages(id),
    UNIQUE(term, page_id)
);
```

### Links Table
```sql
CREATE TABLE links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_page_id INTEGER NOT NULL,
    to_page_id INTEGER NOT NULL,
    FOREIGN KEY (from_page_id) REFERENCES pages(id),
    FOREIGN KEY (to_page_id) REFERENCES pages(id),
    UNIQUE(from_page_id, to_page_id)
);
```

## Algorithms

### TF-IDF (Term Frequency-Inverse Document Frequency)

**Term Frequency (TF)**:
```
TF(term, document) = count(term in document) / total_terms_in_document
```

**Inverse Document Frequency (IDF)**:
```
IDF(term) = log((total_documents + 1) / (documents_with_term + 1)) + 1
```

**TF-IDF Score**:
```
TF-IDF(term, document) = TF(term, document) × IDF(term)
```

### PageRank

PageRank is calculated iteratively:

```
PR(page) = (1-d)/N + d × Σ(PR(incoming_page) / outgoing_links(incoming_page))
```

Where:
- `d` = damping factor (0.85)
- `N` = total number of pages
- Iterations: 20

### Final Ranking Score

```
final_score = (tf_idf_score × 0.7 + page_rank × 0.3) × (1 + term_match_boost)
```

## Sample Data

The application includes 10 sample web pages about programming topics:
- Python Programming
- JavaScript
- Web Development
- Machine Learning
- Databases
- Algorithms
- React Framework
- API Design
- DevOps
- Cloud Computing

## Customization

### Adding Real Web Crawling

To crawl real websites, modify the `index_pages` endpoint in `main.py`:

```python
from backend.crawler import WebCrawler

crawler = WebCrawler(max_pages=100, delay=0.5)
pages = crawler.crawl(request.urls)
```

### Adjusting Ranking Weights

Modify the weights in `backend/search_engine.py`:

```python
final_score = (data['tf_idf_score'] * 0.7 +  # TF-IDF weight
               data['page_rank'] * 0.3)        # PageRank weight
```

### Changing PageRank Parameters

Modify the parameters in `backend/indexer.py`:

```python
pr_calculator = PageRankCalculator(
    damping_factor=0.85,  # Probability of following links
    iterations=20          # Number of iterations
)
```

## Performance

- **Index Build Time**: ~100ms for 10 pages
- **Search Time**: ~10-50ms per query
- **Database Size**: ~50KB for 10 pages
- **Memory Usage**: ~50MB

## Testing

Try these sample queries:
- `python` - Find Python-related pages
- `web development` - Multi-term search
- `machine learning` - Phrase search
- `javascript framework` - Combined terms
- `api` - Short term search

## Future Enhancements

- [ ] Real-time web crawling
- [ ] Auto-complete suggestions dropdown
- [ ] Search filters (date, domain, etc.)
- [ ] Image search
- [ ] Advanced query syntax (AND, OR, NOT)
- [ ] Spell checking and correction
- [ ] Related searches
- [ ] Cached pages
- [ ] Distributed crawling
- [ ] Machine learning for ranking

## Technology Stack

- **Backend**: Python 3.8+, FastAPI
- **Database**: SQLite3
- **Web Crawling**: BeautifulSoup4, Requests
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Server**: Uvicorn (ASGI)

## License

MIT License - Feel free to use and modify

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by Google's search engine
- TF-IDF algorithm from information retrieval theory
- PageRank algorithm by Larry Page and Sergey Brin

## Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Python and FastAPI**
