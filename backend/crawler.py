import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Optional
import time
import re


class WebCrawler:
    """Web crawler for indexing pages."""

    def __init__(self, max_pages: int = 100, delay: float = 0.5):
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SearchEngineBot/1.0'
        })

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and crawlable."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme) and \
                   parsed.scheme in ['http', 'https']
        except:
            return False

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

    def fetch_page(self, url: str) -> Optional[Dict]:
        """Fetch and parse a web page."""
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()

            # Only process HTML content
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return None

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract title
            title = soup.title.string if soup.title else url

            # Extract meta description
            meta_desc = ''
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag['content']

            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()

            # Extract text content
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines
                     for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)

            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                normalized = self.normalize_url(absolute_url)

                if self.is_valid_url(normalized):
                    links.append(normalized)

            return {
                'url': url,
                'title': title,
                'content': content,
                'meta_description': meta_desc,
                'links': links
            }

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def crawl(self, start_urls: List[str]) -> List[Dict]:
        """Crawl web pages starting from seed URLs."""
        to_visit = list(start_urls)
        crawled_pages = []

        while to_visit and len(self.visited_urls) < self.max_pages:
            url = to_visit.pop(0)
            normalized_url = self.normalize_url(url)

            if normalized_url in self.visited_urls:
                continue

            print(f"Crawling: {normalized_url} ({len(self.visited_urls) + 1}/{self.max_pages})")

            page_data = self.fetch_page(normalized_url)

            if page_data:
                self.visited_urls.add(normalized_url)
                crawled_pages.append(page_data)

                # Add new links to visit
                for link in page_data['links']:
                    normalized_link = self.normalize_url(link)
                    if normalized_link not in self.visited_urls and \
                       normalized_link not in to_visit:
                        to_visit.append(normalized_link)

            # Be polite
            time.sleep(self.delay)

        return crawled_pages


# Sample data for testing without actual web crawling
SAMPLE_PAGES = [
    {
        'url': 'http://example.com/python',
        'title': 'Python Programming Language',
        'content': 'Python is a high-level, interpreted programming language. '
                   'Python is known for its simple syntax and readability. '
                   'Python is widely used in web development, data science, machine learning, and automation. '
                   'Popular Python frameworks include Django, Flask, and FastAPI.',
        'meta_description': 'Learn about Python programming language',
        'links': []
    },
    {
        'url': 'http://example.com/javascript',
        'title': 'JavaScript - The Language of the Web',
        'content': 'JavaScript is a versatile programming language primarily used for web development. '
                   'JavaScript runs in the browser and enables interactive web pages. '
                   'Modern JavaScript frameworks include React, Vue, and Angular. '
                   'Node.js allows JavaScript to run on the server side.',
        'meta_description': 'JavaScript programming guide',
        'links': []
    },
    {
        'url': 'http://example.com/webdev',
        'title': 'Web Development Guide',
        'content': 'Web development involves creating websites and web applications. '
                   'Frontend development uses HTML, CSS, and JavaScript. '
                   'Backend development can use Python, Node.js, Ruby, or other languages. '
                   'Full-stack developers work on both frontend and backend.',
        'meta_description': 'Complete guide to web development',
        'links': []
    },
    {
        'url': 'http://example.com/machine-learning',
        'title': 'Machine Learning Basics',
        'content': 'Machine learning is a subset of artificial intelligence. '
                   'Machine learning algorithms learn from data to make predictions. '
                   'Popular machine learning libraries include TensorFlow, PyTorch, and scikit-learn. '
                   'Python is the most popular language for machine learning.',
        'meta_description': 'Introduction to machine learning',
        'links': []
    },
    {
        'url': 'http://example.com/databases',
        'title': 'Database Systems',
        'content': 'Databases store and organize data for applications. '
                   'SQL databases include PostgreSQL, MySQL, and SQLite. '
                   'NoSQL databases include MongoDB, Redis, and Cassandra. '
                   'Database design is crucial for application performance.',
        'meta_description': 'Learn about database systems',
        'links': []
    },
    {
        'url': 'http://example.com/algorithms',
        'title': 'Algorithms and Data Structures',
        'content': 'Algorithms are step-by-step procedures for solving problems. '
                   'Common algorithms include sorting, searching, and graph traversal. '
                   'Data structures organize data efficiently. '
                   'Understanding algorithms is essential for programming interviews.',
        'meta_description': 'Guide to algorithms and data structures',
        'links': []
    },
    {
        'url': 'http://example.com/react',
        'title': 'React Framework',
        'content': 'React is a JavaScript library for building user interfaces. '
                   'React uses a component-based architecture. '
                   'React virtual DOM provides efficient rendering. '
                   'React is maintained by Facebook and widely used in modern web development.',
        'meta_description': 'Learn React for web development',
        'links': []
    },
    {
        'url': 'http://example.com/api-design',
        'title': 'REST API Design',
        'content': 'REST APIs provide a standard way for applications to communicate. '
                   'RESTful APIs use HTTP methods like GET, POST, PUT, and DELETE. '
                   'API design principles include consistency, versioning, and proper status codes. '
                   'Tools like FastAPI and Express make API development easier.',
        'meta_description': 'Best practices for REST API design',
        'links': []
    },
    {
        'url': 'http://example.com/devops',
        'title': 'DevOps Practices',
        'content': 'DevOps combines development and operations. '
                   'DevOps practices include continuous integration and continuous deployment. '
                   'Popular DevOps tools include Docker, Kubernetes, and Jenkins. '
                   'DevOps improves software delivery speed and reliability.',
        'meta_description': 'Introduction to DevOps',
        'links': []
    },
    {
        'url': 'http://example.com/cloud',
        'title': 'Cloud Computing',
        'content': 'Cloud computing provides on-demand computing resources. '
                   'Major cloud providers include AWS, Google Cloud, and Azure. '
                   'Cloud services include infrastructure, platforms, and software. '
                   'Cloud computing enables scalable and flexible applications.',
        'meta_description': 'Guide to cloud computing',
        'links': []
    }
]


def get_sample_data():
    """Get sample data for testing."""
    return SAMPLE_PAGES
