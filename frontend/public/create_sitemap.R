
# Setup ----------------------------------------

library(rairtable) # https://github.com/matthewjrogers/rairtable
set_airtable_api_key('API KEY HERE', install = TRUE)


# Manually Import Non-Airtable URLs ---------------------------------

all_main_pages <- c(
  "https://alpha.cold.global/",
  "https://alpha.cold.global/about",
  "https://alpha.cold.global/about/about-cold",
  "https://alpha.cold.global/about/endorsements",
  "https://alpha.cold.global/about/press",
  "https://alpha.cold.global/about/supporters",
  "https://alpha.cold.global/about/team",
  "https://alpha.cold.global/contact",
  "https://alpha.cold.global/disclaimer",
  "https://alpha.cold.global/learn",
  "https://alpha.cold.global/learn/data-sets",
  "https://alpha.cold.global/learn/faq",
  "https://alpha.cold.global/learn/glossary",
  "https://alpha.cold.global/learn/methodology",
  "https://alpha.cold.global/learn/open-educational-resources"
  )

all_main_pages <- as.data.frame(all_main_pages)
all_main_pages <- all_main_pages %>% rename(url = all_main_pages)

# Import Data from Airtable ---------------------------------

all_court_decisions <- airtable('Court Decisions', 'appz9Ei9mu9NIGmbK')
all_court_decisions <- read_airtable(all_court_decisions)


# Setup URLs ---------------------------------

court_decision_url <- "https://alpha.cold.global/court-decision/"


# Create List ---------------------------------

all_court_decision_urls <- all_court_decisions %>% 
  select(ID) %>% 
  mutate(url = paste0(court_decision_url, ID)) %>% 
  select(url)

all_urls <- all_main_pages %>% 
  rbind(all_court_decision_urls)


# Export ---------------------------------

write.table(all_urls,
            "sitemap.txt",
            sep="\t",
            row.names = F,
            col.names = F,
            quote = F)
