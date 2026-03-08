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
      key: "question",
      label: "Question",
      emptyValueBehavior: {
        action: "display",
        fallback: "No question available",
        fallbackClass: "text-gray-500",
      },
    },
    {
      key: "answer",
      label: "Answer",
      emptyValueBehavior: {
        action: "display",
        fallback: "No answer available",
        fallbackClass: "text-gray-500",
      },
    },
    {
      key: "moreInformation",
      label: "More Information",
      emptyValueBehavior: {
        action: "hide",
      },
    },
    {
      key: "domesticLegalProvisions",
      label: "Domestic Legal Provisions",
      emptyValueBehavior: {
        action: "hide",
      },
    },
    {
      key: "domesticInstrumentsId",
      label: "Domestic Instruments ID",
      emptyValueBehavior: {
        action: "hide",
      },
    },
    {
      key: "literature",
      label: "Literature",
      emptyValueBehavior: {
        action: "hide",
      },
    },
    {
      key: "lastModified",
      label: "Last Modified",
      emptyValueBehavior: {
        action: "hide",
      },
    },
  ],
  valueClassMap: {
    question: "result-value-medium",
    answer: "result-value-large",
    lastModified: "result-value-small",
    moreInformation: "result-value-small",
  },
  gridConfig: {
    question: {
      columnSpan: "md:col-span-4",
      startColumn: "md:col-start-1",
    },
    answer: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-6",
    },
    lastModified: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-6",
    },
    source: {
      columnSpan: "md:col-span-4",
      startColumn: "md:col-start-8",
    },
  },
  getAnswerClass: (answer) => {
    return answer === "Yes" || answer === "No"
      ? "result-value-large"
      : "result-value-medium";
  },
};

export const courtDecisionCardConfig = {
  keyLabelPairs: [
    {
      key: "caseTitle",
      label: "Case Title",
      emptyValueBehavior: {
        action: "display",
        fallback: "No case title available",
        getFallback: (data) => {
          const title = data.caseTitle;
          return !title || title.trim() === "NA"
            ? data.caseCitation || "No case citation available"
            : title;
        },
      },
    },
    {
      key: "publicationDateIso",
      label: "Date",
      emptyValueBehavior: {
        action: "display",
        fallback: "No date available",
      },
    },
    {
      key: "instance",
      label: "Instance",
      emptyValueBehavior: {
        action: "display",
        fallback: "No instance available",
      },
    },
    {
      key: "choiceOfLawIssue",
      label: "Choice of Law Issue",
      emptyValueBehavior: {
        action: "hide",
      },
    },
  ],
  valueClassMap: {
    caseTitle: "result-value-medium",
    publicationDateIso: "result-value-small",
    instance: "result-value-small",
    choiceOfLawIssue: "result-value-small",
  },
  gridConfig: {
    caseTitle: {
      columnSpan: "md:col-span-3",
      startColumn: "md:col-start-1",
    },
    date: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-4",
    },
    instance: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-6",
    },
    choiceOfLaw: {
      columnSpan: "md:col-span-4",
      startColumn: "md:col-start-8",
    },
  },
};

export const legislationCardConfig = {
  keyLabelPairs: [
    {
      key: "titleInEnglish",
      label: "Name",
      emptyValueBehavior: {
        action: "display",
        fallback: "No title available",
      },
    },
    {
      key: "abbreviation",
      label: "Abbreviation",
      emptyValueBehavior: {
        action: "hide",
      },
    },
    {
      key: "date",
      label: "Date",
      emptyValueBehavior: {
        action: "hide",
      },
    },
  ],
  valueClassMap: {
    titleInEnglish: "result-value-medium",
    abbreviation: "result-value-small",
    date: "result-value-small",
  },
  gridConfig: {
    title: {
      columnSpan: "md:col-span-4",
      startColumn: "md:col-start-1",
    },
    date: {
      columnSpan: "md:col-span-1",
      startColumn: "md:col-start-6",
    },
    abbreviation: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-8",
    },
  },
  processData: (data) => {
    if (!data) return null;
    return {
      ...data,
      themes: data.domesticLegalProvisionsThemes,
    };
  },
};

export const regionalInstrumentCardConfig = {
  keyLabelPairs: [
    {
      key: "abbreviation",
      label: "Abbreviation",
      emptyValueBehavior: {
        action: "display",
        fallback: "No title available",
      },
    },
    {
      key: "date",
      label: "Date",
      emptyValueBehavior: {
        action: "hide",
      },
    },
    {
      key: "title",
      label: "Title",
      emptyValueBehavior: {
        action: "hide",
      },
    },
  ],
  valueClassMap: {
    abbreviation: "result-value-medium",
    date: "result-value-small",
    title: "result-value-small",
  },
  gridConfig: {
    abbreviation: {
      columnSpan: "md:col-span-3",
      startColumn: "md:col-start-1",
    },
    title: {
      columnSpan: "md:col-span-4",
      startColumn: "md:col-start-4",
    },
    date: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-4",
    },
  },
};

export const internationalInstrumentCardConfig = {
  keyLabelPairs: [
    {
      key: "name",
      label: "Title",
      emptyValueBehavior: {
        action: "display",
        fallback: "No title available",
      },
    },
    {
      key: "date",
      label: "Date",
      emptyValueBehavior: {
        action: "hide",
      },
    },
  ],
  valueClassMap: {
    name: "result-value-medium",
    date: "result-value-small",
  },
  gridConfig: {
    name: {
      columnSpan: "md:col-span-3",
      startColumn: "md:col-start-1",
    },
    date: {
      columnSpan: "md:col-span-2",
      startColumn: "md:col-start-4",
    },
  },
};

export const literatureCardConfig = {
  keyLabelPairs: [
    {
      key: "title",
      label: "Title",
      emptyValueBehavior: {
        action: "display",
        fallback: "No title available",
      },
    },
    {
      key: "author",
      label: "Author(s)",
      emptyValueBehavior: {
        action: "display",
        fallback: "No author available",
      },
    },
    {
      key: "publicationYear",
      label: "Date",
      emptyValueBehavior: {
        action: "display",
        fallback: "No year available",
      },
    },
    {
      key: "publicationTitle",
      label: "Publication",
      emptyValueBehavior: {
        action: "display",
        fallback: "No publication available",
        shouldDisplay: (data) => data.itemType !== "book",
      },
    },
    {
      key: "publisher",
      label: "Publisher",
      emptyValueBehavior: {
        action: "display",
        fallback: "No publisher available",
        shouldDisplay: (data) => data.itemType === "book",
      },
    },
  ],
  valueClassMap: {
    title: "result-value-medium",
    author: "result-value-small",
    publicationYear: "result-value-small",
    publicationTitle: "result-value-small",
    publisher: "result-value-small",
  },
  gridConfig: {
    title: {
      columnSpan: "md:col-span-4",
      startColumn: "md:col-start-1",
    },
    authorYear: {
      columnSpan: "md:col-span-8",
      startColumn: "md:col-start-5",
    },
  },
  processData: (data) => {
    if (!data) return null;
    return {
      ...data,
      themes: data.themes,
    };
  },
};
