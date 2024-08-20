document.getElementById('searchButton').addEventListener('click', function() {
    const searchInput = document.getElementById('searchInput').value;
    const isSemanticSearch = document.getElementById('toggleSwitch').checked;

    if (!searchInput) {
        alert('Please enter search text.');
        return;
    }

    fetchResults(searchInput, isSemanticSearch);
});

function fetchResults(searchText, isSemanticSearch) {
    const query = {
        search_string: searchText,
        use_semantic_search: isSemanticSearch
    };

    fetch('http://127.0.0.1:5000/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(query)
    })
    .then(response => response.json())
    .then(data => displayResults(data, isSemanticSearch))
    .catch(error => console.error('Error:', error));
}

function displayResults(data, isSemanticSearch) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear previous results

    const totalMatches = document.createElement('p');
    totalMatches.textContent = `Total Matches: ${data.total_matches}`;
    resultsContainer.appendChild(totalMatches);

    if (isSemanticSearch) {
        // Handle semantic search results
        data.results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';

            Object.keys(result).forEach(key => {
                const keyElement = document.createElement('div');
                keyElement.className = 'result-key';
                keyElement.textContent = formatTitle(key);
                resultItem.appendChild(keyElement);

                const valueElement = createCollapsibleContent(result[key]);
                resultItem.appendChild(valueElement);
            });

            resultsContainer.appendChild(resultItem);
        });
    } else {
        // Handle regular search results
        Object.keys(data.tables).forEach(table => {
            const tableData = data.tables[table];
            const matches = tableData.matches;

            const header = document.createElement('h2');
            header.textContent = formatTitle(table) + ` (Matches: ${matches})`;
            resultsContainer.appendChild(header);

            const results = tableData.results;
            for (const key in results) {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';

                const resultData = results[key];
                for (const resultKey in resultData) {
                    const keyElement = document.createElement('div');
                    keyElement.className = 'result-key';
                    keyElement.textContent = formatTitle(resultKey);
                    resultItem.appendChild(keyElement);

                    const valueElement = createCollapsibleContent(resultData[resultKey]);
                    resultItem.appendChild(valueElement);
                }
                resultsContainer.appendChild(resultItem);
            }
        });
    }
}

function formatTitle(title) {
    return title.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function createCollapsibleContent(text) {
    const COLLAPSE_THRESHOLD = 100; // Adjust this threshold as needed
    const container = document.createElement('div');
    
    if (typeof text === 'string' && text.length > COLLAPSE_THRESHOLD) {
        const preview = document.createElement('span');
        preview.textContent = text.slice(0, COLLAPSE_THRESHOLD) + '... ';
        container.appendChild(preview);

        const expandLink = document.createElement('span');
        expandLink.className = 'collapsible';
        expandLink.textContent = 'Show more';
        container.appendChild(expandLink);

        const fullText = document.createElement('div');
        fullText.className = 'collapsible-content';
        fullText.textContent = text;
        fullText.style.display = 'none';
        container.appendChild(fullText);

        expandLink.addEventListener('click', function() {
            if (fullText.style.display === 'none') {
                fullText.style.display = 'block';
                expandLink.style.display = 'none';
                preview.style.display = 'none';

                const collapseLink = document.createElement('span');
                collapseLink.className = 'collapsible';
                collapseLink.textContent = 'Show less';
                fullText.appendChild(collapseLink);

                collapseLink.addEventListener('click', function() {
                    fullText.style.display = 'none';
                    expandLink.style.display = 'inline';
                    preview.style.display = 'inline';
                    fullText.removeChild(collapseLink);
                });
            }
        });
    } else {
        container.textContent = text;
    }

    return container;
}
