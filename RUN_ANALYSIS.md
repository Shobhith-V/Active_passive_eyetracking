# Running the Eye-Tracking Analysis Pipeline

## Prerequisites

1. **R must be installed** on your system
   - Download from: https://cran.r-project.org/
   - Make sure R is added to your system PATH

2. **Required R packages** (will be installed automatically if missing):
   - `readxl` - For reading Excel files
   - `dplyr`, `tidyr` - Data manipulation
   - `mgcv` - GAMM modeling
   - `itsadug` - GAMM interpretation
   - `ggplot2` - Visualization
   - `DHARMa` - Model diagnostics
   - `emmeans` - Estimated marginal means

## Running the Analysis

### Option 1: Using the Batch Script (Windows)

Simply double-click `run_analysis.bat` or run from command prompt:
```cmd
cd Active_passive_eyetracking
run_analysis.bat
```

### Option 2: Run Scripts Individually

Run each script in sequence using Rscript:

```cmd
cd Active_passive_eyetracking
Rscript scripts/01_load_and_clean_data.R
Rscript scripts/02_create_analysis_variables.R
Rscript scripts/03_merge_datasets.R
Rscript scripts/04_data_quality.R
Rscript scripts/05_exploratory_analysis.R
Rscript scripts/06_visualizations.R
Rscript scripts/07_gamm_fixation_duration.R
Rscript scripts/08_gamm_dwell_time.R
Rscript scripts/09_gamm_saccade.R
Rscript scripts/10_gamm_time_to_first_fixation.R
Rscript scripts/11_model_diagnostics.R
Rscript scripts/12_effect_sizes.R
Rscript scripts/13_results_visualization.R
Rscript scripts/14_generate_report.R
```

### Option 3: Using RStudio

1. Open RStudio
2. Set working directory to `Active_passive_eyetracking`
3. Open and run each script in sequence (01 through 14)

## Troubleshooting

### Rscript not found

If you get "Rscript not found" error:

1. **Find your R installation:**
   - Common locations:
     - `C:\Program Files\R\R-4.x.x\bin\Rscript.exe`
     - `C:\Program Files\R\R-3.x.x\bin\Rscript.exe`

2. **Add R to PATH:**
   - Open System Properties → Environment Variables
   - Add R's `bin` directory to PATH
   - Example: `C:\Program Files\R\R-4.3.2\bin`

3. **Or use full path:**
   ```cmd
   "C:\Program Files\R\R-4.3.2\bin\Rscript.exe" scripts/01_load_and_clean_data.R
   ```

### Missing R Packages

If you get package errors, install them in R:
```r
install.packages(c("readxl", "dplyr", "tidyr", "mgcv", "itsadug", 
                   "ggplot2", "DHARMa", "emmeans"))
```

## Output Locations

After running the pipeline, results will be in:

- **Processed Data:** `data/processed/`
- **Models:** `models/`
- **Plots:** `plots/`
- **Results:** `results/`

## Notes

- The scripts will create necessary directories automatically
- Each script can be run independently (they load previous outputs)
- Check console output for progress and any warnings

