/**
 * Configuration for page sections and their display properties
 * Each page has its own configuration object with:
 * - keyLabelPairs: Array of {key, label} pairs defining the sections
 * - valueClassMap: Object mapping API keys to CSS classes for styling
 */

export const literatureConfig = {
    keyLabelPairs: [
        { key: 'Title', label: 'Title' },
        { key: 'Author', label: 'Author' },
        { key: 'Editor', label: 'Editor' },
        { key: 'Publication Year', label: 'Year' },
        { key: 'Publication Title', label: 'Publication' }
    ],
    valueClassMap: {
        Title: 'result-value-medium',
        Author: 'result-value-small',
        Editor: 'result-value-small',
        'Publication Year': 'result-value-small',
        'Publication Title': 'result-value-small',
        Themes: 'result-value-small',
        'Manual Tags': 'result-value-small',
        Jurisdictions: 'result-value-small',
        'Related Literature': 'result-value-small'
    }
}

export const jurisdictionConfig = {
    keyLabelPairs: [
        { key: 'Name', label: 'Jurisdiction' },
        { key: 'Jurisdictional Differentiator', label: 'Jurisdictional Differentiator' },
        { key: 'Specialist', label: 'Specialists' },
        { key: 'Literature', label: 'Related Literature' }
    ],
    valueClassMap: {
        Name: 'result-value-medium',
        'Jurisdictional Differentiator': 'result-value-small',
        Literature: 'result-value-small'
    }
}

export const questionConfig = {
    keyLabelPairs: [
        { key: 'Question', label: 'Question' },
        { key: 'Answer', label: 'Answer' },
        { key: 'More Information', label: 'More Information' },
        { key: 'Domestic Legal Provisions', label: 'Source' },
        { key: 'Court Decisions ID', label: 'related cases' },
        { key: 'Related Literature', label: '' }
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
        { key: 'Title (in English)', label: 'Name' },
        { key: 'Official Title', label: 'Official Title' },
        { key: 'Date', label: 'Date' },
        { key: 'Abbreviation', label: 'Abbreviation' },
        { key: 'Entry Into Force', label: 'Entry Into Force' },
        { key: 'Publication Date', label: 'Publication Date' },
        { key: 'Domestic Legal Provisions', label: 'Selected Provisions' }
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
        { key: 'Case Title', label: 'Case Title' },
        { key: 'Date', label: 'Date' },
        { key: 'Instance', label: 'Instance' },
        { key: 'Abstract', label: 'Abstract' },
        { key: 'Relevant Facts', label: 'Relevant Facts' },
        { key: 'Choice of Law Issue', label: 'Choice of Law Issue' },
        { key: "Court's Position", label: "Court's Position" },
        { key: 'Text of the Relevant Legal Provisions', label: 'Text of the Relevant Legal Provisions' },
        { key: 'Case Citation', label: 'Case Citation' },
        { key: 'Related Literature', label: '' }
    ],
    valueClassMap: {
        'Case Title': 'result-value-medium',
        Date: 'result-value-small',
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