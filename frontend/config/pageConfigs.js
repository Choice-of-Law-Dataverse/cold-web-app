/**
 * Configuration for page sections and their display properties
 * Each page has its own configuration object with:
 * - keyLabelPairs: Array of {key, label} pairs defining the sections
 * - valueClassMap: Object mapping API keys to CSS classes for styling
 */

// Literature Page
export const literatureConfig = {
  keyLabelPairs: [
    {
      key: 'Title',
      label: 'Title',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No title available',
      },
    },
    {
      key: 'Author',
      label: 'Author',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No author available',
      },
    },
    {
      key: 'Editor',
      label: 'Editor',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Publication Year',
      label: 'Year',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No year available',
      },
    },
    {
      key: 'Publication Title',
      label: 'Publication',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No publication available',
        shouldDisplay: (data) => data['Item Type'] !== 'book',
      },
    },
    {
      key: 'Publisher',
      label: 'Publisher',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No publisher available',
        shouldDisplay: (data) => data['Item Type'] === 'book',
      },
    },
    {
      key: 'Abstract Note',
      label: 'Abtract',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    Title: 'result-value-medium',
    Author: 'result-value-small',
    Editor: 'result-value-small',
    'Publication Year': 'result-value-small',
    'Publication Title': 'result-value-small',
    Publisher: 'result-value-small',
    Themes: 'result-value-small',
    Jurisdictions: 'result-value-small',
    'Related Literature': 'result-value-small',
    'Abstract Note': 'result-value-small whitespace-pre-line',
  },
}

// Jurisdiction Page
export const jurisdictionConfig = {
  keyLabelPairs: [
    {
      key: 'Jurisdiction Summary',
      label: 'Summary',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Jurisdictional Differentiator',
      label: 'Jurisdictional Differentiator',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    // Removed Legal Family from here, now only in card header
    {
      key: 'Specialist',
      label: 'Specialists',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No specialists available',
      },
    },
    {
      key: 'Related Literature',
      label: 'Related Literature',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    'Jurisdiction Summary': 'result-value-small',
    'Jurisdictional Differentiator': 'result-value-small',
    // 'Legal Family': 'result-value-small', // not needed in detail section
    'Related Literature': 'result-value-small',
  },
}

// Question Page
export const questionConfig = {
  keyLabelPairs: [
    {
      key: 'Question',
      label: 'Question',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No question available',
      },
    },
    {
      key: 'Answer',
      label: 'Answer',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No answer available',
      },
    },
    {
      key: 'More Information',
      label: 'More Information',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Domestic Legal Provisions',
      label: 'Source',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No source available',
      },
    },
    {
      key: 'Court Decisions ID',
      label: 'Related Court Decisions',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No related court decisions',
      },
    },
    {
      key: 'Related Literature',
      label: 'Related Literature',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No related literature',
      },
    },
  ],
  valueClassMap: {
    Question: 'result-value-medium',
    Answer: 'result-value-large',
    'Domestic Legal Provisions': 'result-value-small',
    'More Information': 'result-value-small whitespace-pre-line',
    'Court Decisions ID': 'result-value-small',
    'Related Literature': 'result-value-small',
  },
}

// Domestic Instrument (formerly Legal Instrument) Page
export const legalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: 'Title (in English)',
      label: 'Name',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No title available',
      },
    },
    {
      key: 'Official Title',
      label: 'Official Title',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No official title available',
      },
    },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'N/A',
        shouldHide: (data) => {
          return data && (data['Entry Into Force'] || data['Publication Date'])
        },
      },
    },
    {
      key: 'Abbreviation',
      label: 'Abbreviation',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Entry Into Force',
      label: 'Entry Into Force',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Publication Date',
      label: 'Publication Date',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Compatible With the HCCH Principles?',
      label: 'Compatible With the HCCH Principles?',
      emptyValueBehavior: {
        action: 'hide',
      },
      valueTransform: (val) => (val === true || val === 'true' ? 'Yes' : ''),
    },
    {
      key: 'Compatible With the UNCITRAL Model Law?',
      label: 'Compatible With the UNCITRAL Model Law?',
      emptyValueBehavior: {
        action: 'hide',
      },
      valueTransform: (val) => (val === true || val === 'true' ? 'Yes' : ''),
    },
    {
      key: 'Domestic Legal Provisions',
      label: 'Selected Provisions',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No provisions available',
      },
    },
    {
      key: 'Amended by',
      label: 'Amended by',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Amends',
      label: 'Amends',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Replaces',
      label: 'Replaces',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Replaced by',
      label: 'Replaced by',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    'Title (in English)': 'result-value-medium',
    'Official Title': 'result-value-small',
    Date: 'result-value-small',
    Abbreviation: 'result-value-small',
    'Entry Into Force': 'result-value-small',
    'Publication Date': 'result-value-small',
    'Domestic Legal Provisions': 'result-value-small',
    'Compatible With the HCCH Principles?': 'result-value-small',
    'Compatible With the UNCITRAL Model Law?': 'result-value-small',
    Themes: 'result-value-small',
    'Manual Tags': 'result-value-small',
    'Related Literature': 'result-value-small',
  },
}

// Regional Instrument Page
export const regionalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: 'Abbreviation',
      label: 'Abbreviation',
      emptyValueBehavior: { action: 'display', fallback: 'No title available' },
    },
    { key: 'Title', label: 'Title', emptyValueBehavior: { action: 'hide' } },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: { action: 'display', fallback: 'N/A' },
    },
    {
      key: 'Specialists',
      label: 'Specialists',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No specialists available',
      },
    },
    {
      key: 'Literature',
      label: 'Related Literature',
      emptyValueBehavior: { action: 'hide' },
    },
    {
      key: 'Regional Legal Provisions',
      label: 'Regional Legal Provisions',
      emptyValueBehavior: { action: 'display', fallback: '' },
    },
  ],
  valueClassMap: {
    Abbreviation: 'result-value-medium',
    Title: 'result-value-small',
    Date: 'result-value-small',
    'Related Literature': 'result-value-small',
    'Regional Legal Provisions': 'result-value-small',
  },
}

// International Instrument Page
export const internationalInstrumentConfig = {
  keyLabelPairs: [
    {
      key: 'Name',
      label: 'Name',
      emptyValueBehavior: { action: 'display', fallback: 'No title available' },
    },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: { action: 'display', fallback: 'N/A' },
    },
    {
      key: 'Specialists',
      label: 'Specialists',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No specialists available',
      },
    },
    {
      key: 'Literature',
      label: 'Related Literature',
      emptyValueBehavior: { action: 'hide' },
    },
    {
      key: 'Selected Provisions',
      label: 'Selected Provisions',
      emptyValueBehavior: { action: 'display', fallback: '' },
    },
  ],
  valueClassMap: {
    Name: 'result-value-medium',
    Date: 'result-value-small',
    'Related Literature': 'result-value-small',
    'Selected Provisions': 'result-value-small',
  },
}

// Court Decision Page
export const courtDecisionConfig = {
  keyLabelPairs: [
    {
      key: 'Case Title',
      label: 'Case Title',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No case title available',
        getFallback: (data) => {
          if (!data) {
            return 'No case citation available'
          }
          const title = data['Case Title']
          return !title || title.trim() === 'NA'
            ? data['Case Citation'] || 'No case citation available'
            : title
        },
      },
    },
    {
      key: 'Publication Date ISO',
      label: 'Date',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No date available',
      },
    },
    {
      key: 'Instance',
      label: 'Instance',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No instance information available',
      },
    },
    {
      key: 'Abstract',
      label: 'Abstract',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No abstract available',
      },
    },
    {
      key: 'Relevant Facts',
      label: 'Relevant Facts',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No relevant facts available',
      },
    },
    {
      key: 'Choice of Law Issue',
      label: 'Choice of Law Issue',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No choice of law issue available',
      },
    },
    {
      key: "Court's Position",
      label: "Court's Position",
      emptyValueBehavior: {
        action: 'display',
        fallback: "No court's position available",
      },
    },
    {
      key: 'Text of the Relevant Legal Provisions',
      label: 'Text of the Relevant Legal Provisions',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No relevant legal provisions available',
      },
    },
    {
      key: 'Case Citation',
      label: 'Case Citation',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No case citation available',
      },
    },
    {
      key: 'Related Questions',
      label: 'Related Questions',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Related Literature',
      label: '',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No related literature available',
      },
    },
  ],
  valueClassMap: {
    'Case Title': 'result-value-medium',
    'Publication Date ISO': 'result-value-small',
    Instance: 'result-value-small',
    Abstract: 'result-value-small whitespace-pre-line',
    'Relevant Facts': 'result-value-small whitespace-pre-line',
    'Choice of Law Issue': 'result-value-small whitespace-pre-line',
    "Court's Position": 'result-value-small whitespace-pre-line',
    'Text of the Relevant Legal Provisions':
      'result-value-small whitespace-pre-line',
    Quote: 'result-value-small',
    'Case Citation': 'result-value-small-citation',
    'Related Literature': 'result-value-small',
    'Related Questions': 'result-value-small',
  },
}

export const aboutNavLinks = [
  { label: 'About CoLD', key: 'about-cold', path: '/about/about-cold' },
  { label: 'Team', key: 'team', path: '/about/team' },
  { label: 'Supporters', key: 'supporters', path: '/about/supporters' },
  { label: 'Endorsements', key: 'endorsements', path: '/about/endorsements' },
  { label: 'Press', key: 'press', path: '/about/press' },
]

export const learnNavLinks = [
  {
    label: 'Open Educational Resources',
    key: 'open-educational-resources',
    path: '/learn/open-educational-resources',
  },
  { label: 'FAQ', key: 'faq', path: '/about/team', path: '/learn/faq' },
  { label: 'Methodology', key: 'methodology', path: '/learn/methodology' },
  { label: 'Glossary', key: 'glossary', path: '/learn/glossary' },
  { label: 'Data Sets', key: 'data-sets', path: '/learn/data-sets' },
]
