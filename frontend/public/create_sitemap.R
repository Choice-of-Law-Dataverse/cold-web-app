
# Setup ----------------------------------------

library(rairtable) # https://github.com/matthewjrogers/rairtable
set_airtable_api_key('API KEY HERE', install = TRUE)


# Manually Import Non-Airtable URLs ---------------------------------

all_main_pages <- c(
  "https://cold.global/",
  "https://cold.global/about",
  "https://cold.global/contact",
  "https://cold.global/disclaimer",
  "https://cold.global/learn",
  "https://cold.global/about/about-cold",
  "https://cold.global/about/endorsements",
  "https://cold.global/about/press",
  "https://cold.global/about/supporters",
  "https://cold.global/about/team",
  "https://cold.global/learn/data-sets",
  "https://cold.global/learn/faq",
  "https://cold.global/learn/glossary",
  "https://cold.global/learn/methodology",
  "https://cold.global/learn/open-educational-resources"
  )

all_main_pages <- as.data.frame(all_main_pages)
all_main_pages <- all_main_pages %>% rename(url = all_main_pages)

# Import Data from Airtable ---------------------------------

cold_base <- 'appz9Ei9mu9NIGmbK'

all_jurisdictions <- airtable('Jurisdictions', cold_base)
all_questions <- airtable('Answers', cold_base)
all_domestic_instruments <- airtable('Domestic Instruments', cold_base)
all_regional_instruments <- airtable('Regional Instruments', cold_base)
all_international_instruments <- airtable('International Instruments', cold_base)
all_court_decisions <- airtable('Court Decisions', cold_base)
all_literature <- airtable('Literature', cold_base)

all_jurisdictions <- read_airtable(all_jurisdictions)
all_questions <- read_airtable(all_questions)
all_domestic_instruments <- read_airtable(all_domestic_instruments)
all_regional_instruments <- read_airtable(all_regional_instruments)
all_international_instruments <- read_airtable(all_international_instruments)
all_court_decisions <- read_airtable(all_court_decisions)
all_literature <- read_airtable(all_literature)


# Setup URLs ---------------------------------

jurisdiction_url <- "https://cold.global/jurisdiction/"
question_url <- "https://cold.global/question/"
domestic_instrument_url <- "https://cold.global/domestic-instrument/"
regional_instrument_url <- "https://cold.global/regional-instrument/"
international_instrument_url <- "https://cold.global/international-instrument/"
court_decision_url <- "https://cold.global/court-decision/"
literature_url <- "https://cold.global/literature/"


# Create List ---------------------------------

all_jurisdiction_urls <- all_jurisdictions %>% 
  select(`Alpha-3 Code`) %>%
  mutate(`Alpha-3 Code` = tolower(`Alpha-3 Code`)) %>% 
  mutate(url = paste0(jurisdiction_url, `Alpha-3 Code`)) %>%
  select(url)

all_question_urls <- all_questions %>% 
  select(ID) %>%
  mutate(url = paste0(question_url, ID)) %>%
  select(url)

all_domestic_instrument_urls <- all_domestic_instruments %>% 
  select(ID) %>%
  mutate(url = paste0(domestic_instrument_url, ID)) %>%
  select(url)

all_regional_instrument_urls <- all_regional_instruments %>% 
  select(ID) %>%
  mutate(url = paste0(regional_instrument_url, ID)) %>%
  select(url)

all_international_instrument_urls <- all_international_instruments %>% 
  select(ID) %>%
  mutate(url = paste0(international_instrument_url, ID)) %>%
  select(url)

all_court_decision_urls <- all_court_decisions %>% 
  select(ID) %>%
  mutate(url = paste0(court_decision_url, ID)) %>%
  select(url)

all_literature_urls <- all_literature %>% 
  select(ID) %>%
  mutate(url = paste0(literature_url, ID)) %>%
  select(url)

all_urls <- all_main_pages %>% 
  rbind(all_jurisdiction_urls) %>% 
  rbind(all_question_urls) %>% 
  rbind(all_domestic_instrument_urls) %>% 
  rbind(all_regional_instrument_urls) %>% 
  rbind(all_international_instrument_urls) %>% 
  rbind(all_court_decision_urls) %>% 
  rbind(all_literature_urls)


# Export ---------------------------------

write.table(all_urls,
            "sitemap.txt",
            # sep="\t",
            row.names = F,
            col.names = F,
            quote = F)
