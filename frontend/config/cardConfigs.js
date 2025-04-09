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
                fallback: 'No question available',
                fallbackClass: 'text-gray-500'
            }
        },
        {
            key: 'Answer',
            label: 'Answer',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No answer available',
                fallbackClass: 'text-gray-500'
            }
        },
        {
            key: 'More Information',
            label: 'More Information',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'NANANA',
                fallbackClass: 'text-gray-500'
            }
        }
    ],
    valueClassMap: {
        Question: 'result-value-medium',
        Answer: 'result-value-large', // This will be overridden by getAnswerClass for Yes/No answers
        'More Information': 'result-value-small'
    },
    gridConfig: {
        question: {
            columnSpan: 'md:col-span-4',
            startColumn: 'md:col-start-1'
        },
        answer: {
            columnSpan: 'md:col-span-2',
            startColumn: 'md:col-start-6'
        },
        source: {
            columnSpan: 'md:col-span-4',
            startColumn: 'md:col-start-8'
        }
    },
    getAnswerClass: (answer) => {
        return answer === 'Yes' || answer === 'No'
            ? 'result-value-large'
            : 'result-value-medium'
    }
}

export const courtDecisionCardConfig = {
    keyLabelPairs: [
        {
            key: 'Case Title',
            label: 'Case Title',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No case title available',
                getFallback: (data) => {
                    const title = data['Case Title']
                    return !title || title.trim() === 'NA'
                        ? data['Case Citation'] || 'No case citation available'
                        : title
                }
            }
        },
        {
            key: 'Choice of Law Issue',
            label: 'Choice of Law Issue',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No choice of law issue available'
            }
        }
    ],
    valueClassMap: {
        'Case Title': 'result-value-medium',
        'Choice of Law Issue': 'result-value-small'
    },
    gridConfig: {
        caseTitle: {
          columnSpan: 'md:col-span-4',
          startColumn: 'md:col-start-1'
        },
        choiceOfLaw: {
          columnSpan: 'md:col-span-6',
          startColumn: 'md:col-start-6'
        }
    }
}

export const legislationCardConfig = {
    keyLabelPairs: [
        {
            key: 'Title (in English)',
            label: 'Title',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No title available'
            }
        },
        {
            key: 'Abbreviation',
            label: 'Abbreviation',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No abbreviation available'
            }
        }
    ],
    valueClassMap: {
        'Title (in English)': 'result-value-medium',
        'Abbreviation': 'result-value-medium'
    },
    gridConfig: {
        title: {
            columnSpan: 'md:col-span-6',
            startColumn: 'md:col-start-1'
        }
    },
    processData: (data) => {
        if (!data) return null
        return {
            ...data,
            Themes: data['Domestic Legal Provisions Themes'] // Map "Themes name" to "Themes"
        }
    }
}

export const literatureCardConfig = {
    keyLabelPairs: [
        {
            key: 'Title',
            label: 'Title',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No title available'
            }
        },
        {
            key: 'Author',
            label: 'Author',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No author available'
            }
        },
        {
            key: 'Publication Year',
            label: 'Year',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No year available'
            }
        },
        {
            key: 'Publication Title',
            label: 'Publication',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No publication available',
                shouldDisplay: (data) => data['Item Type'] !== 'book'
            }
        },
        {
            key: 'Publisher',
            label: 'Publisher',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No publisher available',
                shouldDisplay: (data) => data['Item Type'] === 'book'
            }
        }
    ],
    valueClassMap: {
        Title: 'result-value-medium',
        Author: 'result-value-small',
        'Publication Year': 'result-value-small',
        'Publication Title': 'result-value-small',
        'Publisher': 'result-value-small'
    },
    gridConfig: {
        title: {
            columnSpan: 'md:col-span-4',
            startColumn: 'md:col-start-1'
        },
        authorYear: {
            columnSpan: 'md:col-span-8',
            startColumn: 'md:col-start-5'
        }
    },
    processData: (data) => {
        if (!data) return null
        return {
            ...data,
            Themes: data['Themes'] // Map "Themes name" to "Themes"
        }
    }
} 