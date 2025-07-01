/**
 * Configuration for search result cards and their display properties
 * Each card type has its own configuration object with:
 * - keyLabelPairs: Array of {key, label} pairs defining the sections
 * - valueClassMap: Object mapping API keys to CSS classes for styling
 * - gridConfig: Object defining the grid layout for the card
 */

// Question Card
export const answerCardConfig = {
  keyLabelPairs: [
    {
      key: 'Question',
      label: 'Question',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No question available',
        fallbackClass: 'text-gray-500',
      },
    },
    {
      key: 'Answer',
      label: 'Answer',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No answer available',
        fallbackClass: 'text-gray-500',
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
      label: 'Domestic Legal Provisions',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Domestic Instruments ID',
      label: 'Domestic Instruments ID',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Literature',
      label: 'Literature',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    Question: 'result-value-medium',
    Answer: 'result-value-large', // This will be overridden by getAnswerClass for Yes/No answers
    'More Information': 'result-value-small',
  },
  gridConfig: {
    question: {
      columnSpan: 'md:col-span-4',
      startColumn: 'md:col-start-1',
    },
    answer: {
      columnSpan: 'md:col-span-2',
      startColumn: 'md:col-start-6',
    },
    source: {
      columnSpan: 'md:col-span-4',
      startColumn: 'md:col-start-8',
    },
  },
  getAnswerClass: (answer) => {
    return answer === 'Yes' || answer === 'No'
      ? 'result-value-large'
      : 'result-value-medium'
  },
}

// Court Decision Card
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
        fallback: 'No instance available',
      },
    },
    {
      key: 'Choice of Law Issue',
      label: 'Choice of Law Issue',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    'Case Title': 'result-value-medium',
    'Publication Date ISO': 'result-value-small',
    Instance: 'result-value-small',
    'Choice of Law Issue': 'result-value-small',
  },
  gridConfig: {
    caseTitle: {
      columnSpan: 'md:col-span-3',
      startColumn: 'md:col-start-1',
    },
    date: {
      columnSpan: 'md:col-span-2',
      startColumn: 'md:col-start-4',
    },
    instance: {
      columnSpan: 'md:col-span-2',
      startColumn: 'md:col-start-6',
    },
    choiceOfLaw: {
      columnSpan: 'md:col-span-4',
      startColumn: 'md:col-start-8',
    },
  },
}

// Domestic Instrument Card (formerly Legal Instrument Card)
export const legislationCardConfig = {
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
      key: 'Abbreviation',
      label: 'Abbreviation',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    'Title (in English)': 'result-value-medium',
    Abbreviation: 'result-value-small',
    Date: 'result-value-small',
  },
  gridConfig: {
    title: {
      columnSpan: 'md:col-span-4',
      startColumn: 'md:col-start-1',
    },
    date: {
      columnSpan: 'md:col-span-1',
      startColumn: 'md:col-start-6',
    },
    abbreviation: {
      columnSpan: 'md:col-span-2',
      startColumn: 'md:col-start-8',
    },
  },
  processData: (data) => {
    if (!data) return null
    return {
      ...data,
      Themes: data['Domestic Legal Provisions Themes'], // Map "Themes name" to "Themes"
    }
  },
}

export const regionalInstrumentCardConfig = {
  keyLabelPairs: [
    {
      key: 'Abbreviation',
      label: 'Abbreviation',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No title available',
      },
    },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Title',
      label: 'Title',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    Abbreviation: 'result-value-medium',
    Date: 'result-value-small',
    Title: 'result-value-small',
  },
  gridConfig: {
    abbreviation: {
      columnSpan: 'md:col-span-3',
      startColumn: 'md:col-start-1',
    },
    title: {
      columnSpan: 'md:col-span-4',
      startColumn: 'md:col-start-4',
    },
    date: {
      columnSpan: 'md:col-span-2',
      startColumn: 'md:col-start-4',
    },
  },
}

export const internationalInstrumentCardConfig = {
  keyLabelPairs: [
    {
      key: 'Name',
      label: 'Title',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No title available',
      },
    },
    {
      key: 'Date',
      label: 'Date',
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    Name: 'result-value-medium',
    Date: 'result-value-small',
  },
  gridConfig: {
    name: {
      columnSpan: 'md:col-span-3',
      startColumn: 'md:col-start-1',
    },
    date: {
      columnSpan: 'md:col-span-2',
      startColumn: 'md:col-start-4',
    },
  },
}

export const literatureCardConfig = {
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
      label: 'Author(s)',
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No author available',
      },
    },
    {
      key: 'Publication Year',
      label: 'Date',
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
  ],
  valueClassMap: {
    Title: 'result-value-medium',
    Author: 'result-value-small',
    'Publication Year': 'result-value-small',
    'Publication Title': 'result-value-small',
    Publisher: 'result-value-small',
  },
  gridConfig: {
    title: {
      columnSpan: 'md:col-span-4',
      startColumn: 'md:col-start-1',
    },
    authorYear: {
      columnSpan: 'md:col-span-8',
      startColumn: 'md:col-start-5',
    },
  },
  processData: (data) => {
    if (!data) return null
    return {
      ...data,
      Themes: data['Themes'], // Map "Themes name" to "Themes"
    }
  },
}
