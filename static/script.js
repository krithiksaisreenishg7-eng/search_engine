// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    // Focus search input on page load
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.focus();
    }

    // Handle "I'm Feeling Lucky" button
    window.feelingLucky = function() {
        const searchInput = document.getElementById('search-input');
        const query = searchInput.value.trim();

        if (!query) {
            alert('Please enter a search query');
            return;
        }

        // Perform search and redirect to first result
        fetch(`/api/search?q=${encodeURIComponent(query)}&limit=1`)
            .then(response => response.json())
            .then(data => {
                if (data.results && data.results.length > 0) {
                    window.location.href = data.results[0].url;
                } else {
                    alert('No results found');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while searching');
            });
    };

    // Auto-suggest functionality (optional enhancement)
    setupAutocomplete();
});

// Setup autocomplete/suggestions
function setupAutocomplete() {
    const searchInputs = document.querySelectorAll('input[name="q"]');

    searchInputs.forEach(input => {
        let timeout = null;

        input.addEventListener('input', function() {
            const query = this.value.trim();

            // Clear previous timeout
            if (timeout) {
                clearTimeout(timeout);
            }

            // Don't show suggestions for very short queries
            if (query.length < 2) {
                return;
            }

            // Debounce the suggestions request
            timeout = setTimeout(() => {
                fetchSuggestions(query, input);
            }, 300);
        });
    });
}

// Fetch search suggestions
function fetchSuggestions(query, inputElement) {
    fetch(`/api/suggestions?q=${encodeURIComponent(query)}&limit=5`)
        .then(response => response.json())
        .then(data => {
            if (data.suggestions && data.suggestions.length > 0) {
                console.log('Suggestions:', data.suggestions);
                // You can implement a dropdown UI here if desired
            }
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
        });
}

// Handle keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Focus search on '/' key
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput && document.activeElement !== searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    }
});

// Add animation to search results
function animateResults() {
    const results = document.querySelectorAll('.result-item');
    results.forEach((result, index) => {
        result.style.opacity = '0';
        result.style.transform = 'translateY(20px)';

        setTimeout(() => {
            result.style.transition = 'all 0.3s ease';
            result.style.opacity = '1';
            result.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// Run animations on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', animateResults);
} else {
    animateResults();
}
