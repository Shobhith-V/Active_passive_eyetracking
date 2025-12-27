# Python Analysis Pipeline

This directory contains Python versions of the R analysis scripts for eye-tracking data analysis.

## Prerequisites

1. **Python 3.8 or higher** must be installed
2. **Required Python packages** (install with pip):

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas numpy openpyxl xlrd matplotlib seaborn
```

## Running the Analysis

### Option 1: Run All Scripts at Once (Recommended)

```bash
python scripts/run_analysis.py
```

This will run all scripts in sequence (01-05).

### Option 2: Run Scripts Individually

Run each script in sequence:

```bash
python scripts/01_load_and_clean_data.py
python scripts/02_create_analysis_variables.py
python scripts/03_merge_datasets.py
python scripts/04_data_quality.py
python scripts/05_exploratory_analysis.py
```

## Script Overview

1. **01_load_and_clean_data.py**: Loads Excel files, extracts participant IDs, selects variables, performs initial cleaning
2. **02_create_analysis_variables.py**: Creates AOI categories, trial identifiers, time windows, and aggregations
3. **03_merge_datasets.py**: Merges fixation, interest area, and saccade datasets
4. **04_data_quality.py**: Checks for missing data, identifies outliers, validates consistency
5. **05_exploratory_analysis.py**: Creates summary statistics and exploratory visualizations

## Notes

- Scripts 07-14 (GAMM modeling) from the R version are not yet converted. These use specialized statistical modeling packages (mgcv in R). Python equivalents would require packages like `pygam`, `statsmodels`, or `scikit-learn` with custom implementations.
- The Python scripts produce the same output files as the R versions, maintaining compatibility with the analysis pipeline.

## Output Files

All output files are saved in the same locations as the R scripts:
- `data/processed/`: Processed CSV files
- `results/`: Analysis results and reports
- `plots/`: Generated visualizations

