
# Setup ----------------------------

library(tidyverse)
library(rstudioapi)

# Getting the path of your current open file
current_path = rstudioapi::getActiveDocumentContext()$path
setwd(dirname(current_path))
library(here)


# Import ----------------------------

# Import Answers table from Airtable
answers <- read.csv(here("frontend", "public", "temp_Answers-All data.csv"))

# Import Jurisdictions
jurisdictions <- read.csv(here("frontend", "public", "temp_Jurisdictions-All data.csv"))


# Preprocessing ----------------------------

jurisdictions <- jurisdictions %>% 
  select(Alpha.3.code, Alpha.2.code) %>%
  rename(iso2 = Alpha.2.code,
         iso3 = Alpha.3.code) %>% 
  distinct(iso3, .keep_all = T)

answers <- answers %>% 
  select(ID, Answer, Alpha.3.code..from.Jurisdiction.) %>% 
  rename(iso3 = Alpha.3.code..from.Jurisdiction.) %>% 
  dplyr::filter(Answer != "No data") %>% 
  dplyr::filter(Answer != "") %>% 
  left_join(jurisdictions, by = "iso3")


# Process Data ----------------------------

distinct_jurisdictions <- answers %>% distinct(iso3)


# Export ----------------------------

# Export unique jurisdictions to text file
write.table(distinct_jurisdictions,
            here("frontend", "public", "temp_answer_coverage.txt"),
            sep = "\n",
            row.names = F,
            col.names = F,
            quote = F)
