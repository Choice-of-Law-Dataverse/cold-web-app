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
    Title: 'result-value-medium section-gap',
    Author: 'result-value-small section-gap',
    Editor: 'result-value-small section-gap',
    'Publication Year': 'result-value-small section-gap',
    'Publication Title': 'result-value-small section-gap',
    Publisher: 'result-value-small section-gap',
    Themes: 'result-value-small section-gap',
    Jurisdictions: 'result-value-small section-gap',
    'Related Literature': 'result-value-small section-gap',
    'Abstract Note': 'result-value-small whitespace-pre-line section-gap',
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
    'Jurisdiction Summary': 'result-value-small section-gap',
    'Jurisdictional Differentiator': 'result-value-small section-gap',
    // 'Legal Family': 'result-value-small', // not needed in detail section
    'Related Literature': 'result-value-small section-gap',
  },
}

// Question Page
// Tooltips for Question Page
import tooltipQuestion from '@/content/info_boxes/question/question.md?raw'
import tooltipAnswer from '@/content/info_boxes/question/answer.md?raw'
import tooltipQuestionRelatedLiterature from '@/content/info_boxes/question/related_literature.md?raw'
import tooltipMoreInformation from '@/content/info_boxes/question/more_information.md?raw'
import tooltipSource from '@/content/info_boxes/question/source.md?raw'
import tooltipOUPBookQuote from '@/content/info_boxes/question/oup_book_quote.md?raw'
import tooltipRelatedCourtDecisions from '@/content/info_boxes/question/related_court_decisions.md?raw'

export const questionConfig = {
  keyLabelPairs: [
    {
      key: 'Question',
      label: 'Question',
      tooltip: tooltipQuestion,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No question available',
      },
    },
    {
      key: 'Answer',
      label: 'Answer',
      tooltip: tooltipAnswer,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No answer available',
      },
    },
    {
      key: 'More Information',
      label: 'More Information',
      tooltip: tooltipMoreInformation,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Domestic Legal Provisions',
      label: 'Source',
      tooltip: tooltipSource,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No source available',
      },
    },
    {
      key: 'OUP Book Quote',
      label: 'OUP Book Quote',
      tooltip: tooltipOUPBookQuote,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Court Decisions ID',
      label: 'Related Court Decisions',
      tooltip: tooltipRelatedCourtDecisions,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No related court decisions',
      },
    },
    {
      key: 'Related Literature',
      label: 'Related Literature',
      tooltip: tooltipQuestionRelatedLiterature,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No related literature',
      },
    },
  ],
  valueClassMap: {
    Question: 'result-value-medium section-gap',
    Answer: 'result-value-large section-gap',
    'Domestic Legal Provisions': 'result-value-small section-gap',
    'More Information': 'result-value-small whitespace-pre-line section-gap',
    'OUP Book Quote': 'result-value-small section-gap',
    'Court Decisions ID': 'result-value-small section-gap',
    'Related Literature': 'result-value-small section-gap',
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
        action: 'hide',
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
    'Title (in English)': 'result-value-medium section-gap',
    'Official Title': 'result-value-small section-gap',
    Date: 'result-value-small section-gap',
    Abbreviation: 'result-value-small section-gap',
    'Entry Into Force': 'result-value-small section-gap',
    'Publication Date': 'result-value-small section-gap',
    'Domestic Legal Provisions': 'result-value-small section-gap',
    'Compatible With the HCCH Principles?': 'result-value-small section-gap',
    'Compatible With the UNCITRAL Model Law?': 'result-value-small section-gap',
    'Amended by': 'result-value-small section-gap',
    Amends: 'result-value-small section-gap',
    Replaces: 'result-value-small section-gap',
    'Replaced by': 'result-value-small section-gap',
    Themes: 'result-value-small section-gap',
    'Manual Tags': 'result-value-small section-gap',
    'Related Literature': 'result-value-small section-gap',
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
    Abbreviation: 'result-value-medium section-gap',
    Title: 'result-value-small section-gap',
    Date: 'result-value-small section-gap',
    'Related Literature': 'result-value-small section-gap',
    'Regional Legal Provisions': 'result-value-small section-gap',
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
    Name: 'result-value-medium section-gap',
    Date: 'result-value-small section-gap',
    'Related Literature': 'result-value-small section-gap',
    'Selected Provisions': 'result-value-small section-gap',
  },
}

// Court Decision Page
// Tooltips for Court Decision Page
import tooltipAbstract from '@/content/info_boxes/court_decision/abstract.md?raw'
import tooltipCaseCitation from '@/content/info_boxes/court_decision/case_citation.md?raw'
import tooltipCaseTitle from '@/content/info_boxes/court_decision/case_title.md?raw'
import tooltipChoiceOfLawIssue from '@/content/info_boxes/court_decision/choice_of_law_issue.md?raw'
import tooltipCourtsPosition from '@/content/info_boxes/court_decision/courts_position.md?raw'
//import tooltipDomesticLegalProvision from '@/content/info_boxes/court_decision/domestic_legal_provision.md?raw'
import tooltipFullText from '@/content/info_boxes/court_decision/full_text.md?raw'
import tooltipInstance from '@/content/info_boxes/court_decision/instance.md?raw'
import tooltipJudgmentDate from '@/content/info_boxes/court_decision/judgment_date.md?raw'
import tooltipPILProvisions from '@/content/info_boxes/court_decision/pil_provisions.md?raw'
import tooltipPublicationDate from '@/content/info_boxes/court_decision/publication_date.md?raw'
import tooltipQuote from '@/content/info_boxes/court_decision/quote.md?raw'
import tooltipCourtDecisionRelatedLiterature from '@/content/info_boxes/court_decision/related_literature.md?raw'
import tooltipRelatedQuestions from '@/content/info_boxes/court_decision/related_questions.md?raw'
import tooltipRelevantFacts from '@/content/info_boxes/court_decision/relevant_facts.md?raw'
import tooltipTextRelevantLegalProvision from '@/content/info_boxes/court_decision/text_relevant_legal_provision.md?raw'

export const courtDecisionConfig = {
  keyLabelPairs: [
    {
      key: 'Case Title',
      label: 'Case Title',
      tooltip: tooltipCaseTitle,
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
      label: 'Publication Date',
      tooltip: tooltipPublicationDate,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No date available',
      },
    },
    {
      key: 'Date of Judgment',
      label: 'Judgment Date',
      tooltip: tooltipJudgmentDate,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Instance',
      label: 'Instance',
      tooltip: tooltipInstance,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No instance information available',
      },
    },
    {
      key: 'Abstract',
      label: 'Abstract',
      tooltip: tooltipAbstract,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Relevant Facts',
      label: 'Relevant Facts',
      tooltip: tooltipRelevantFacts,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'PIL Provisions',
      label: 'PIL Provisions',
      tooltip: tooltipPILProvisions,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Text of the Relevant Legal Provisions',
      label: 'Text of the Relevant Legal Provisions',
      tooltip: tooltipTextRelevantLegalProvision,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Choice of Law Issue',
      label: 'Choice of Law Issue',
      tooltip: tooltipChoiceOfLawIssue,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: "Court's Position",
      label: "Court's Position",
      tooltip: tooltipCourtsPosition,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Quote',
      label: 'Quote',
      tooltip: tooltipQuote,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Case Citation',
      label: 'Case Citation',
      tooltip: tooltipCaseCitation,
      emptyValueBehavior: {
        action: 'display',
        fallback: 'No case citation available',
      },
    },
    {
      key: 'Original Text',
      label: 'Full Text',
      tooltip: tooltipFullText,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Related Literature',
      label: 'Related Literature',
      tooltip: tooltipCourtDecisionRelatedLiterature,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
    {
      key: 'Related Questions',
      label: 'Related Questions',
      tooltip: tooltipRelatedQuestions,
      emptyValueBehavior: {
        action: 'hide',
      },
    },
  ],
  valueClassMap: {
    'Case Title': 'result-value-medium section-gap',
    'Publication Date ISO': 'result-value-small section-gap',
    'Date of Judgment': 'result-value-small section-gap',
    Instance: 'result-value-small section-gap',
    Abstract: 'result-value-small whitespace-pre-line section-gap',
    'Relevant Facts': 'result-value-small whitespace-pre-line section-gap',
    'PIL Provisions': 'result-value-small section-gap',
    'Text of the Relevant Legal Provisions':
      'result-value-small whitespace-pre-line section-gap',
    'Choice of Law Issue': 'result-value-small whitespace-pre-line section-gap',
    "Court's Position": 'result-value-small whitespace-pre-line section-gap',
    Quote: 'result-value-small section-gap',
    'Case Citation': 'result-value-small-citation section-gap',
    'Original Text': 'result-value-small section-gap',
    'Related Literature': 'result-value-small section-gap',
    'Related Questions': 'result-value-small section-gap',
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
