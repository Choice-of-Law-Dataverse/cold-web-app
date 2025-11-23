# Flags provided by https://github.com/hampusborgos/country-flags use ISO2 naming
#  This script renames them to ISO3, with the exception of EU, Kosovo and GB

# Setup
library(here)
library(countrycode)

# Set your folder path here
folder_path <- here("Desktop", "country-flags-main", "svg-iso3")

# Get all SVG files with ISO2 codes (e.g., 'us.svg')
svg_files <- list.files(folder_path, pattern = "\\.svg$", full.names = TRUE)

# Loop through each file
for (file_path in svg_files) {
  # Extract the base name (e.g., 'us' from 'us.svg')
  file_name <- tools::file_path_sans_ext(basename(file_path))

  # Convert to ISO3 using countrycode
  iso3_code <- countrycode(file_name, origin = "iso2c", destination = "iso3c")

  # Only rename if valid ISO3 code was found
  if (!is.na(iso3_code)) {
    new_file_path <- file.path(folder_path, paste0(tolower(iso3_code), ".svg"))
    file.rename(file_path, new_file_path)
    cat("Renamed:", basename(file_path), "→", basename(new_file_path), "\n")
  } else {
    cat("Skipping:", basename(file_path), "- ISO2 code not recognized.\n")
  }
}
