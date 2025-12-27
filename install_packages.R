# Install required packages to user library
# This script creates a user library if needed and installs all required packages

# Create user library path
user_lib <- file.path(Sys.getenv("USERPROFILE"), "Documents", "R", "win-library", 
                      paste(R.version$major, strsplit(R.version$minor, "\\.")[[1]][1], sep = "."))

# Create directory if it doesn't exist
dir.create(user_lib, recursive = TRUE, showWarnings = FALSE)

# Add to library paths
.libPaths(c(user_lib, .libPaths()))

# Required packages
required_packages <- c(
  "readxl",
  "dplyr",
  "tidyr",
  "mgcv",
  "itsadug",
  "ggplot2",
  "DHARMa",
  "emmeans",
  "stringr"
)

# Check which packages are missing
missing <- required_packages[!sapply(required_packages, requireNamespace, quietly = TRUE)]

if (length(missing) > 0) {
  cat("Installing missing packages:", paste(missing, collapse = ", "), "\n")
  install.packages(missing, lib = user_lib, repos = "https://cran.r-project.org")
} else {
  cat("All required packages are already installed.\n")
}

# Verify installation
cat("\nVerifying package installation...\n")
for (pkg in required_packages) {
  if (requireNamespace(pkg, quietly = TRUE)) {
    cat("✓", pkg, "is installed\n")
  } else {
    cat("✗", pkg, "failed to install\n")
  }
}

cat("\nPackage installation complete!\n")



