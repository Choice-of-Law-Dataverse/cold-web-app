
# Create JSON file used for detecting jurisdictions in search suggestions

## Setup --------------------------------------------

library(dplyr)
library(here)
library(rairtable)
library(rgpt3)


## Import and process relevant jurisdictions --------

# Jurisdictions from Airtable
all_jurisdictions <- airtable('Jurisdictions', 'appz9Ei9mu9NIGmbK', view = 'Relevant JDs')
all_jurisdictions <- read_airtable(all_jurisdictions)

# Process DF
all_jurisdictions_process <- all_jurisdictions %>% 
  select("Alpha-3 Code", Name) %>% 
  rename(iso3 = "Alpha-3 Code",
         name = Name)


## Create DF for ChatGPT prompt ---------------------

prompt_df <- all_jurisdictions_process %>% 
  mutate(prompt_role_var = "user") %>% # Set role
  mutate(prompt_content_var = paste0("Please tell me the demonym(s) for '", name, "'. Only return the demonym(s), nothing else."))

# Create sample for testing
prompt_df <- prompt_df %>% slice_sample(n = 5)


## Query ChatGPT -----------------------------------

# https://github.com/ben-aaron188/rgpt3?tab=readme-ov-file#getting-started
# Setup and test ChatGPT API
rgpt_authenticate(here("frontend", "assets", "access_key.txt"))
# rgpt_test_completion(verbose = T)

chatgpt_output <- rgpt(
  prompt_role_var = prompt_df$prompt_role_var,
  prompt_content_var = prompt_df$prompt_content_var,
  param_seed = 123,
  id_var = prompt_df$iso3,
  param_output_type = "complete",
  param_model = "gpt-4o-mini-2024-07-18", # https://platform.openai.com/docs/models
  param_max_tokens = 15,
  param_temperature = 0,
  param_n = 1)

# Save output to file
# Get and format the current timestamp to prevent overwriting files when saving RData locally
timestamp <- Sys.time()
formatted_timestamp <- format(timestamp, "%Y%m%d_%H%M%S")
file_name <- paste0("chatgpt_output_df_", formatted_timestamp, ".rds")
saveRDS(chatgpt_output, file = here("frontend", "assets", file_name))
chatgpt_output <- readRDS(here("frontend", "assets", "chatgpt_output_df_20250407_164025.rds"))

# Clean ChatGPT output
chatgpt_output <- chatgpt_output[[1]]
chatgpt_output <- chatgpt_output %>% 
  select(id, gpt_content) %>% 
  rename(iso3 = id,
         denonym = gpt_content)
