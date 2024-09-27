import json
import numpy as np
from config import Config
from .database import Database
from .embeddings import EmbeddingService
from utils.utils import filter_na, parse_results, flatten_and_transform_data
from utils.sorter import Sorter

class SearchService:
    def __init__(self):
        #self.db = Database(Config.AZURE_POSTGRESQL_DUMMY_CONN_STRING)
        self.db = Database(Config.SQL_CONN_STRING)
        self.test = Config.TEST
        self.sorter = Sorter()

    def basic_search(self, search_string):
        all_entries = self.db.get_all_entries()

        # Check if the database retrieval failed without an exception
        if all_entries is None:
            return json.dumps({
                f"{self.test}_error": "Failed to retrieve data from the database. Please try again later."
            })

        results = {}
        total_matches = 0
        search_terms = search_string.lower().split()

        for table, entries in all_entries.items():
            matching_entries = [
                entry for entry in entries
                if all(any(search_term in str(value).lower() for value in entry.values()) for search_term in search_terms)
            ]
            if matching_entries:
                results[table] = {
                    'matches': len(matching_entries),
                    'results': matching_entries
                }
                total_matches += len(matching_entries)

        final_results = {
            'test': self.test,
            'total_matches': total_matches,
            'tables': results
            }
        # Sort data based on "Case rank" and completeness
        sorted_results = self.sorter.sort_by_priority_and_completeness(final_results)

        return filter_na(parse_results(sorted_results))

    def filtered_search(self, search_string, filter_string):
        return f"{self.test}...foo"

    def semantic_search(self, search_string):
        return f"{self.test}...foo"

    def curated_search(self, search_string):
        all_entries = self.db.get_entries_from_tables(['Answers', 'Court decisions'])

        # Check if the database retrieval failed without an exception
        if all_entries is None:
            return json.dumps({
                f"{self.test}_error": "Failed to retrieve data from the database. Please try again later."
            })

        # Pre-selection of columns for each table
        selected_columns = {
            'Answers': [
                'ID', 'Name (from Jurisdiction)', 'Questions', 'Answer', 'More information', 
                'Legal provision articles', 'Secondary legal provision articles', 
                'Legislation titles', 'Case titles'
            ],
            'Court decisions': [
                'ID', 'Case', 'Jurisdiction Names', 'Abstract', 'Content', 
                'Additional information', 'Themes', 'Observations', 'Relevant facts / Summary of the case', 
                'Relevant rules of law involved', 'Choice of law issue', 'Court\'s position', 
                'Text of the relevant legal provisions', 'Quote', 'Translated excerpt', 
                'Case rank', 'Pinpoint facts', 'Pinpoint rules', 'Pinpoint CoL', 'Answer IDs'
            ]
        }

        results = {}
        total_matches = 0
        search_terms = search_string.lower().split()

        for table, entries in all_entries.items():
            # Filter out only the relevant columns
            filtered_entries = [
                {key: entry[key] for key in selected_columns[table] if key in entry}
                for entry in entries
            ]

            matching_entries = [
                entry for entry in filtered_entries
                if all(any(search_term in str(value).lower() for value in entry.values()) for search_term in search_terms)
            ]
            if matching_entries:
                results[table] = {
                    'matches': len(matching_entries),
                    'results': matching_entries
                }
                total_matches += len(matching_entries)
        
        #print(results)

        final_results = {
            'test': self.test,
            'total_matches': total_matches,
            'tables': results#sort_by_priority_and_completeness(results) # Sort data based on "Case rank" and completeness
            }

        return self.sorter.sorting_chain(filter_na(parse_results(final_results)))

    def curated_details_search(self, table, id):
        print(table)
        print(id)
        if table == 'Legal provisions' or table == 'Court decisions':
            final_results = self.db.get_entry_by_id(table, id)
            return filter_na(parse_results(final_results))
            """
            SELECT *
            FROM "Legal provisions"
            WHERE "Name" = 'Swi-148 Art. 117';
            "table": "Legal provisions",
            "id": "Swi-148 Art. 117"
            """
        else:
            return filter_na(parse_results({"error": "this table does not exist or if you are sure it does please ask Simon to implement the detailed search for this table"}))
            """
            SELECT *
            FROM "Court decisions"
            WHERE "ID" = 'CHE-1017';
            "table": "Court decisions",
            "id": "CHE-1017"
            """
        
    def full_text_search(self, search_string):
        # Prepare the SQL query with dynamic search string input
        query = f"""
            -- Search in "Answers" table
            select 
            'Answers' as source_table,               -- Column to indicate the source table
            -- mutual columns
            "ID" as id,
            "Questions" as questions,
            "Record ID" as record_id,
            "Themes" as themes,
            -- answers columns
            "Alpha-3 code (from Jurisdiction)" as alpha_3_a,
            "Answer" as answer_a,
            "Answer Rank" as answer_rank_a,
            "Case titles" as case_titles_a,
            "Cases" as cases_a,
            "Created time" as created_time_a,
            "data type sample" as data_type_sample_a,
            "Interesting answer" as interesting_answer_a,
            "Jurisdiction" as jurisdiction_a,
            "Jurisdictions copy" as jurisdictions_copy_a,
            "Keyword" as keyword_a,
            "Legal provision articles" as legal_provisions_articles_a,
            "Legislation" as legislation_a,
            "Legislation titles" as legislation_titles_a,
            "More information" as more_information_a,
            "Name (from Jurisdiction)" as name_from_jurisdiction_a,
            "OUP Book Quotation" as oup_book_quotation_a,
            "Question" as question_a,
            "Relevant provisions" as relevant_provisions_a,
            "Secondary legal provision articles" as secondary_legal_provision_articles_a,
            "Secondary legal provisions" as secondary_legal_provisions_a,
            "test" as test_a,
            "Theme Code (from Question)" as theme_code_from_question_a,
            "Themes (from Question)" as themes_from_question_a,
            "To review?" as to_review_a,
            "Type (from Jurisdiction)" as type_from_jurisdiction_a,
            -- court decision columns
            NULL as abstract_cd,
            NULL as additional_information_cd,
            NULL as answer_ids_cd,
            NULL as answers_cd,
            NULL as ap_themes_cd,
            NULL as case_cd,
            NULL as case_rank_cd,
            NULL as choice_of_law_issue_cd,
            NULL as content_cd,
            NULL as copyright_issues_cd,
            NULL as courts_position_cd,
            NULL as id_number_cd,
            NULL as jurisdiction_from_forms_cd,
            NULL as jurisdiction_name_cd,
            NULL as jurisdiction_names_cd,
            NULL as jurisdictions_cd,
            NULL as observations_cd,
            NULL as official_source_pdf_cd,
            NULL as official_source_url_cd,
            NULL as pinpoint_col_cd,
            NULL as pinpoint_facts_cd,
            NULL as pinpoint_rules_cd,
            NULL as questions_2_cd,
            NULL as quote_cd,
            NULL as region_from_jurisdictions_cd,
            NULL as relevant_facts_summary_of_the_case_cd,
            NULL as relevant_rules_of_law_involved_cd,
            NULL as selected_case_cd,
            NULL as text_of_the_relevant_legal_provisions_cd,
            NULL as translated_excerpt_cd,
            NULL as type_from_jurisdictions_cd,
            ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
            ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) as rank
            from "Answers"
            where search @@ websearch_to_tsquery('english', '{search_string}')
            or search @@ websearch_to_tsquery('simple', '{search_string}')

            union all

            -- Search in "Court decisions" table
            select 
            'Court decisions' as source_table,       -- Indicate the source table
            -- mutual columns
            "ID" as id,
            "Questions" as questions,
            "Record ID" as record_id,
            "Themes" as themes,
            -- answers columns
            NULL as alpha_3_a,
            NULL as answer_a,
            NULL as answer_rank_a,
            NULL as case_titles_a,
            NULL as cases_a,
            NULL as created_time_a,
            NULL as data_type_sample_a,
            NULL as interesting_answer_a,
            NULL as jurisdiction_a,
            NULL as jurisdictions_copy_a,
            NULL as keyword_a,
            NULL as legal_provisions_articles_a,
            NULL as legislation_a,
            NULL as legislation_titles_a,
            NULL as more_information_a,
            NULL as name_from_jurisdiction_a,
            NULL as oup_book_quotation_a,
            NULL as question_a,
            NULL as relevant_provisions_a,
            NULL as secondary_legal_provision_articles_a,
            NULL as secondary_legal_provisions_a,
            NULL as test_a,
            NULL as theme_code_from_question_a,
            NULL as themes_from_question_a,
            NULL as to_review_a,
            NULL as type_from_jurisdiction_a,
            -- court decision columns
            "Abstract" as abstract_cd,
            "Additional information" as additional_information_cd,
            CAST("Answer IDs" AS text) as answer_ids_cd,  -- Cast to text
            "Answers" as answers_cd,
            "AP themes" as ap_themes_cd,
            "Case" as case_cd,
            "Case rank" as case_rank_cd,
            "Choice of law issue" as choice_of_law_issue_cd,
            "Content" as content_cd,
            "Copyright issues" as copyright_issues_cd,
            "Court's position" as courts_position_cd,
            "ID-number" as id_number_cd,
            "Jurisdiction (from forms)" as jurisdiction_from_forms_cd,
            "Jurisdiction Name" as jurisdiction_name_cd,
            "Jurisdiction Names" as jurisdiction_names_cd,
            "Jurisdictions" as jurisdictions_cd,
            "Observations" as observations_cd,
            "Official Source (PDF)" as official_source_pdf_cd,
            "Official Source (URL)" as official_source_url_cd,
            "Pinpoint CoL" as pinpoint_col_cd,
            "Pinpoint facts" as pinpoint_facts_cd,
            "Pinpoint rules" as pinpoint_rules_cd,
            "Questions 2" as questions_2_cd,
            "Quote" as quote_cd,
            "Region (from Jurisdictions)" as region_from_jurisdictions_cd,
            "Relevant facts / Summary of the case" as relevant_facts_summary_of_the_case_cd,
            "Relevant rules of law involved" as relevant_rules_of_law_involved_cd,
            "Selected case" as selected_case_cd,
            "Text of the relevant legal provisions" as text_of_the_relevant_legal_provisions_cd,
            "Translated excerpt" as translated_excerpt_cd,
            CAST("Type (from Jurisdictions)" AS text) as type_from_jurisdictions_cd,  -- Ensure type matches
            ts_rank(search, websearch_to_tsquery('english', '{search_string}')) +
            ts_rank(search, websearch_to_tsquery('simple', '{search_string}')) as rank
            from "Court decisions"
            where search @@ websearch_to_tsquery('english', '{search_string}')
            or search @@ websearch_to_tsquery('simple', '{search_string}')

            -- Combine results and order by rank
            order by rank desc;
        """

        # Execute the SQL query
        all_entries = self.db.execute_query(query)

        # Check if the query returned any results
        if not all_entries:
            return json.dumps({
                f"{self.test}_error": "No results found for your search."
            })

        # Parse the results into the desired format
        results = {
            "test": self.test,
            "total_matches": len(all_entries),
            "results": all_entries  # Combine all results into one list
        }

        # Return parsed results
        return filter_na(parse_results(results))
