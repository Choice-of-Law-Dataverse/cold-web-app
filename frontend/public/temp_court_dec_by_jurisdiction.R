
# Setup ----------------------------

library(tidyverse)
library(rstudioapi)
library(jsonlite)

# Getting the path of your current open file
current_path = rstudioapi::getActiveDocumentContext()$path
setwd(dirname(current_path))
library(here)


# Import ----------------------------

# Import Court Decisions table from Airtable
court_decisions <- read.csv(here("frontend", "public", "temp_Court decisions-Court Decisions by Jurisdiction Web App Bar Chart.csv"))


# Data Processing ----------------------------

# Create top 10 list
count_jurisdictions <- court_decisions %>% 
  separate_rows(Jurisdiction.Names, sep = ", ") %>% # Separate EU onto separate lines
  group_by(Jurisdiction.Names) %>% 
  count(Jurisdiction.Names) %>% 
  rename(jurisdiction = Jurisdiction.Names) %>% 
  arrange(desc(n)) %>% 
  head(10) %>% 
  arrange(n)

# Add search URL
count_jurisdictions <- count_jurisdictions %>% 
  mutate(url = paste0("/search?jurisdiction=", jurisdiction, "&type=Court+Decisions")) %>% 
  mutate(url = gsub(" ", "+", url))


# Export ----------------------------

write_json(count_jurisdictions, here("frontend", "public", "count_jurisdictions.json"))
