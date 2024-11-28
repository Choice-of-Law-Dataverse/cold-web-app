
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


# Preprocessing ----------------------------

answers <- answers %>% 
  select(ID, Answer, Alpha.3.code..from.Jurisdiction.) %>% 
  rename(jurisdiction = Alpha.3.code..from.Jurisdiction.) %>% 
  dplyr::filter(Answer != "No data") %>% 
  dplyr::filter(Answer != "") 


# Process Data ----------------------------

distinct_jurisdictions <- answers %>% distinct(jurisdiction)


# Export ----------------------------

# Export unique jurisdictions to text file
write.table(distinct_jurisdictions,
            here("frontend", "public", "temp_answer_coverage.txt"),
            sep = "\n",
            row.names = F,
            col.names = F,
            quote = F)
