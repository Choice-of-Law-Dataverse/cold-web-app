document.getElementById('searchButton').addEventListener('click', function() {
    const searchInput = document.getElementById('searchInput').value;
    const selectedCategories = Array.from(document.querySelectorAll('.category-checkbox:checked')).map(checkbox => checkbox.value);

    if (!searchInput) {
        alert('Please enter search text.');
        return;
    }

    fetchResults(searchInput, selectedCategories);
});

function fetchResults(searchText, categories) {
    const query = {
        search_string: searchText
    };

    if (categories.length > 0) {
        query.filter_string = categories.join(',');
    }

    fetch('http://127.0.0.1:5000/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(query)
    })
    .then(response => response.json())
    .then(data => displayResults(data))
    .catch(error => console.error('Error:', error));
}

function displayResults(data) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = ''; // Clear previous results

    const totalMatches = document.createElement('p');
    totalMatches.textContent = `Total Matches: ${data.total_matches}`;
    resultsContainer.appendChild(totalMatches);

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

function formatTitle(title) {
    return title.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
}

function createCollapsibleContent(text) {
    const COLLAPSE_THRESHOLD = 100; // Adjust this threshold as needed
    const container = document.createElement('div');
    
    if (text.length > COLLAPSE_THRESHOLD) {
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
