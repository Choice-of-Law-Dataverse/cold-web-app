/**
 * Configuration for page sections and their display properties
 * Each page has its own configuration object with:
 * - keyLabelPairs: Array of {key, label} pairs defining the sections
 * - valueClassMap: Object mapping API keys to CSS classes for styling
 */

export const literatureConfig = {
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
            key: 'Editor',
            label: 'Editor',
            emptyValueBehavior: {
                action: 'hide'
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
        },
        {
            key: 'Url',
            label: 'Link',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Abstract Note',
            label: 'Abtract',
            emptyValueBehavior: {
                action: 'hide'
            }
        }
    ],
    valueClassMap: {
        Title: 'result-value-medium',
        Author: 'result-value-small',
        Editor: 'result-value-small',
        'Publication Year': 'result-value-small',
        'Publication Title': 'result-value-small',
        Publisher: 'result-value-small',
        Themes: 'result-value-small',
        'Manual Tags': 'result-value-small',
        Jurisdictions: 'result-value-small',
        'Related Literature': 'result-value-small',
        'Abstract Note': 'result-value-small'
    }
}

export const jurisdictionConfig = {
    keyLabelPairs: [
        {
            key: 'Name',
            label: 'Jurisdiction',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No jurisdiction name available'
            }
        },
        {
            key: 'Jurisdictional Differentiator',
            label: 'Jurisdictional Differentiator',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Specialist',
            label: 'Specialists',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No specialists available'
            }
        },
        {
            key: 'Literature',
            label: 'Related Literature',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No related literature available'
            }
        }
    ],
    valueClassMap: {
        Name: 'result-value-medium',
        'Jurisdictional Differentiator': 'result-value-small',
        Literature: 'result-value-small'
    }
}

export const questionConfig = {
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
            key: 'More Information',
            label: 'More Information',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Domestic Legal Provisions',
            label: 'Source',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No source available'
            }
        },
        {
            key: 'Court Decisions ID',
            label: 'Related Court Decisions',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No related cases'
            }
        },
        {
            key: 'Related Literature',
            label: '',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No related literature available'
            }
        }
    ],
    valueClassMap: {
        Question: 'result-value-medium',
        Answer: 'result-value-large',
        'Domestic Legal Provisions': 'result-value-small',
        'Court Decisions ID': 'result-value-small'
    }
}

export const legalInstrumentConfig = {
    keyLabelPairs: [
        {
            key: 'Title (in English)',
            label: 'Name',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No title available'
            }
        },
        {
            key: 'Official Title',
            label: 'Official Title',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Date',
            label: 'Date',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'N/A',
                shouldHide: (data) => {
                    return data['Entry Into Force'] || data['Publication Date']
                }
            }
        },
        {
            key: 'Abbreviation',
            label: 'Abbreviation',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Entry Into Force',
            label: 'Entry Into Force',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Publication Date',
            label: 'Publication Date',
            emptyValueBehavior: {
                action: 'hide'
            }
        },
        {
            key: 'Domestic Legal Provisions',
            label: 'Selected Provisions',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No provisions available'
            }
        }
    ],
    valueClassMap: {
        'Title (in English)': 'result-value-medium',
        'Official Title': 'result-value-small',
        Date: 'result-value-small',
        'Entry Into Force': 'result-value-small',
        'Publication Date': 'result-value-small',
        'Domestic Legal Provisions': 'result-value-small',
        Themes: 'result-value-small',
        'Manual Tags': 'result-value-small',
        'Related Literature': 'result-value-small'
    }
}

export const courtDecisionConfig = {
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
            key: 'Publication Date ISO',
            label: 'Date',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'N/A'
            }
        },
        {
            key: 'Instance',
            label: 'Instance',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No instance information available'
            }
        },
        {
            key: 'Abstract',
            label: 'Abstract',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No abstract available'
            }
        },
        {
            key: 'Relevant Facts',
            label: 'Relevant Facts',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No relevant facts available'
            }
        },
        {
            key: 'Choice of Law Issue',
            label: 'Choice of Law Issue',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No choice of law issue available'
            }
        },
        {
            key: "Court's Position",
            label: "Court's Position",
            emptyValueBehavior: {
                action: 'display',
                fallback: "No court's position available"
            }
        },
        {
            key: 'Text of the Relevant Legal Provisions',
            label: 'Text of the Relevant Legal Provisions',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No relevant legal provisions available'
            }
        },
        {
            key: 'Case Citation',
            label: 'Case Citation',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No case citation available'
            }
        },
        {
            key: 'Related Literature',
            label: '',
            emptyValueBehavior: {
                action: 'display',
                fallback: 'No related literature available'
            }
        }
    ],
    valueClassMap: {
        'Case Title': 'result-value-medium',
        'Publication Date ISO': 'result-value-small',
        Instance: 'result-value-small',
        Abstract: 'result-value-small',
        'Relevant Facts': 'result-value-small',
        'Choice of Law Issue': 'result-value-small',
        "Court's Position": 'result-value-small',
        'Text of the Relevant Legal Provisions': 'result-value-small',
        'Case Citation': 'result-value-small',
        'Related Literature': 'result-value-small'
    }
} 