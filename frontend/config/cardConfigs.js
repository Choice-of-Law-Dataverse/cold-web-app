/**
 * Configuration for search result cards and their display properties
 * Each card type has its own configuration object with:
 * - keyLabelPairs: Array of {key, label} pairs defining the sections
 * - valueClassMap: Object mapping API keys to CSS classes for styling
 * - gridConfig: Object defining the grid layout for the card
 */

export const answerCardConfig = {
    keyLabelPairs: [
        {
            key: 'Question',
            label: 'Question',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No question available'
            }
        },
        {
            key: 'Answer',
            label: 'Answer',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No answer available'
            }
        },
        {
            key: 'Legal provision articles',
            label: 'Source',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No source available'
            }
        }
    ],
    valueClassMap: {
        Question: 'result-value-medium',
        Answer: 'result-value-large', // This will be overridden by getAnswerClass for Yes/No answers
        'Legal provision articles': 'result-value-small'
    },
    gridConfig: {
        question: {
            columnSpan: 4,
            startColumn: 1
        },
        answer: {
            columnSpan: 2,
            startColumn: 6
        },
        source: {
            columnSpan: 4,
            startColumn: 8
        }
    },
    getAnswerClass: (answer) => {
        return answer === 'Yes' || answer === 'No'
            ? 'result-value-large'
            : 'result-value-medium'
    }
} 