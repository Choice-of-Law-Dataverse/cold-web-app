## How the PostgreSQL Full Text Search Works
PostgreSQL, also called Postgres, is a relational database. Relational database means, that data is stored in a structured format, representing tables and columns.
Postgres has an integrated feature called "Full Text Search", which allows to query the database and the data entries stored within by using textual queries (as opposed to using Structured Query Language (SQL), which has sophisticated methods of querying databases that are just as manifold in what can be achieved with them as they are complex in handling).

### General functionality
The Postgres Full Text Search works by comparing an input document (textual user query) with the data found in the database. It is unfeasible to use the raw data as it would be found in the database directly. Instead, the individual entries from a database table have to be translated into a list of documents. The following preparation steps make it possible to use the Postgres Full Text Search feature:

1. **creating searchable documents**

Take every row of a table you want to search. Each of these rows has to be turned into a searchable document. To make a row searchable, you first select the columns you deem fit for including their entries in the searchable content. Then, you transform the text into a list of tokens, more specifically: lexemes (basically word stems). This list of lexemes has been cleaned for stop words and each lexeme is complemented with its position in the original text. Imagine you had a sentence *"The court has decided on party autonomy and arbitration in Switzerland."*. This sentence would be transformed into a list that looks like this: *'arbitr':9 'autonomi':7 'court':2 'decid':4 'parti':6 'switzerland':11*
```
SELECT to_tsvector('The court has decided on party autonomy and arbitration in Switzerland.');
```

2. **parsing textual user queries**

This list can now be used for comparison. To compare it with a textual user query, each query will have to undergo a transformation process similar as in step 1. Searching for *"court decision on party autonomy"* would thus be turned into *'court' & 'decis' & 'parti' & 'autonomi'*. Note that for user queries, the position of words within the original text is not stored.
```
SELECT to_tsquery('court & decision & on & party & autonomy');
```

3. **matching documents with queries**

Finally, we can match the transformed query with all searchable documents in list form available and return whether there is infact a match or not. For some further granularity, we can score each comparison by measuring how relevant each document is to the query.
Following the previous examples, matching and ranking the query from step 2 with the searchable document from step 1, returns a ranking score of *0.25948015*.
Simple comparison:
```
SELECT to_tsquery('court & decision & on & party & autonomy') @@ to_tsvector('The court has decided on party autonomy and arbitration in Switzerland.');
```
Ranking:
```
SELECT
    ts_rank(
        to_tsvector('The court has decided on party autonomy and arbitration in Switzerland.'),
        to_tsquery('court & decision & on & party & autonomy')
		--to_tsquery('party & autonomy')
		)
```

### Implementation in CoLD
The way in which the Postgres Full Text Search feature has been implemented is by enabling Full Text Search for multiple tables in order to search each of them with the same query. The Full Text Search then returns a joint list of results with data entries from all searched tables in order of how well their ranking score matches the textual user query.
Here I am providing an overview for which columns have been selected with which priority for the tables that can be searched using the full text feature. Note that each column to be included for text search can be weighted using weights (A, B, C, D), with A being the highest and D the lowest weight.

1. **"Answers" table**
- Questions (A)
- Name (from Jurisdiction) (A)
- More information (B)
- Themes (C)

2. **"Court decisions" table**
- Case (A)
- Jurisdiction Names (A)
- English translation (B)
- Additional information (C)

3. **"Legislation" table**
- Title (in English) (A)
- Official title (A)
- Jurisdiction name (B)
- Publication date (B)
- Entry into force (B)
- Full text of the provisions (C)
- Full text original (from Legal provisions) (C)
- Full text english (from Legal provisions) (C)

For every row in each table, the respective combination of the values from all specified columns becomes one searchable document. For each table, the match between search query and searchable documents is made separately. Once the matches and ranks are calculated for each table, they are joined into one list. This list is the final result of the search results.