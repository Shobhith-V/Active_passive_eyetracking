@echo off
REM Batch script to run the eye-tracking analysis pipeline
REM This script runs all R scripts in sequence

echo Starting Eye-Tracking Analysis Pipeline...
echo.

REM Check if Rscript is available
where Rscript >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Rscript not found in PATH
    echo Please install R from https://cran.r-project.org/
    echo Or add R to your PATH environment variable
    echo.
    echo Common R installation paths:
    echo   C:\Program Files\R\R-4.x.x\bin
    echo   C:\Program Files\R\R-3.x.x\bin
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

echo Running Script 01: Load and Clean Data...
Rscript scripts/01_load_and_clean_data.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 01
    pause
    exit /b 1
)

echo.
echo Running Script 02: Create Analysis Variables...
Rscript scripts/02_create_analysis_variables.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 02
    pause
    exit /b 1
)

echo.
echo Running Script 03: Merge Datasets...
Rscript scripts/03_merge_datasets.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 03
    pause
    exit /b 1
)

echo.
echo Running Script 04: Data Quality Checks...
Rscript scripts/04_data_quality.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 04
    pause
    exit /b 1
)

echo.
echo Running Script 05: Exploratory Analysis...
Rscript scripts/05_exploratory_analysis.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 05
    pause
    exit /b 1
)

echo.
echo Running Script 06: Visualizations...
Rscript scripts/06_visualizations.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 06
    pause
    exit /b 1
)

echo.
echo Running Script 07: GAMM Fixation Duration...
Rscript scripts/07_gamm_fixation_duration.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 07
    pause
    exit /b 1
)

echo.
echo Running Script 08: GAMM Dwell Time...
Rscript scripts/08_gamm_dwell_time.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 08
    pause
    exit /b 1
)

echo.
echo Running Script 09: GAMM Saccade...
Rscript scripts/09_gamm_saccade.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 09
    pause
    exit /b 1
)

echo.
echo Running Script 10: GAMM Time to First Fixation...
Rscript scripts/10_gamm_time_to_first_fixation.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 10
    pause
    exit /b 1
)

echo.
echo Running Script 11: Model Diagnostics...
Rscript scripts/11_model_diagnostics.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 11
    pause
    exit /b 1
)

echo.
echo Running Script 12: Effect Sizes...
Rscript scripts/12_effect_sizes.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 12
    pause
    exit /b 1
)

echo.
echo Running Script 13: Results Visualization...
Rscript scripts/13_results_visualization.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 13
    pause
    exit /b 1
)

echo.
echo Running Script 14: Generate Report...
Rscript scripts/14_generate_report.R
if %ERRORLEVEL% NEQ 0 (
    echo ERROR in script 14
    pause
    exit /b 1
)

echo.
echo ========================================
echo Analysis Pipeline Complete!
echo ========================================
echo.
echo Results are available in:
echo   - data/processed/
echo   - models/
echo   - plots/
echo   - results/
echo.
pause



