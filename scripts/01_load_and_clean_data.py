# %% Data Loading and Initial Cleaning
# Script: 01_load_and_clean_data.py
# Purpose: Load all Excel files from three report types, extract participant IDs,
#          select relevant variables, and perform initial cleaning

import pandas as pd
import numpy as np
import os
import re
from pathlib import Path

# Set working directory to project root
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directories
os.makedirs("data/processed", exist_ok=True)

# %% Define file paths
fixation_dir = "reports/fixation"
interest_area_dir = "reports/interest_area"
saccade_dir = "reports/saccade_reports"

# %% Function to extract participant ID from filename
def extract_participant_id(filename):
    """
    Extract participant ID from filename.
    Pattern: edf##_YYYY_MM_DD_HH_MM.xls or P##_YYYY_MM_DD_HH_MM.xls
    """
    pattern = r"(edf\d+|P\d+)_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}\.xls"
    match = re.search(pattern, filename)
    if match:
        # Extract the participant ID part (edf## or P##)
        participant_id = re.search(r"(edf\d+|P\d+)", match.group(0))
        if participant_id:
            return participant_id.group(0)
    return None

# %% Load Fixation Reports
print("Loading fixation reports...")
fixation_files = [f for f in Path(fixation_dir).glob("*.xls")]
print(f"Found {len(fixation_files)} fixation files")

fixation_data_list = []

for i, file_path in enumerate(fixation_files, 1):
    filename = file_path.name
    participant_id = extract_participant_id(filename)
    
    if participant_id is None:
        print(f"Warning: Could not extract participant ID from {filename}")
        continue
    
    try:
        # Read file - these are actually tab-separated UTF-16 files, not Excel
        # Try reading as UTF-16 tab-separated first, fall back to Excel if that fails
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-16-le', dtype=str, low_memory=False)
        except (UnicodeDecodeError, pd.errors.ParserError):
            # Fallback to Excel reader
            df = pd.read_excel(file_path, dtype=str, engine='xlrd')
        
        # Add participant ID and filename
        df['participant_id'] = participant_id
        df['data_file'] = filename
        
        # Select relevant variables from fixation reports
        relevant_vars = [
            # Participant and trial identifiers
            "participant_id", "data_file", "TRIAL_INDEX", "TRIAL_LABEL", "TRIAL_START_TIME",
            # Fixation metrics
            "CURRENT_FIX_DURATION", "CURRENT_FIX_INDEX", "CURRENT_FIX_START", "CURRENT_FIX_END",
            "CURRENT_FIX_X", "CURRENT_FIX_Y",
            # Interest area information
            "CURRENT_FIX_INTEREST_AREA_LABEL", "CURRENT_FIX_INTEREST_AREA_ID",
            "CURRENT_FIX_INTEREST_AREA_INDEX", "CURRENT_FIX_INTEREST_AREA_DWELL_TIME",
            "CURRENT_FIX_INTEREST_AREA_FIX_COUNT",
            # Trial-level information
            "TRIAL_FIXATION_TOTAL", "sentence", "voice_id", "image_id", "stim_id",
            "image", "stimulus_file", "session_var", "exp_id", "language", "audio"
        ]
        
        # Select only variables that exist in the dataframe
        vars_to_select = [v for v in relevant_vars if v in df.columns]
        df_selected = df[vars_to_select].copy()
        
        # Convert numeric columns
        numeric_cols = [
            "CURRENT_FIX_DURATION", "CURRENT_FIX_INDEX", "CURRENT_FIX_START",
            "CURRENT_FIX_END", "CURRENT_FIX_X", "CURRENT_FIX_Y",
            "TRIAL_INDEX", "TRIAL_START_TIME", "TRIAL_FIXATION_TOTAL",
            "CURRENT_FIX_INTEREST_AREA_ID", "CURRENT_FIX_INTEREST_AREA_INDEX",
            "CURRENT_FIX_INTEREST_AREA_DWELL_TIME", "CURRENT_FIX_INTEREST_AREA_FIX_COUNT"
        ]
        
        for col in numeric_cols:
            if col in df_selected.columns:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
        
        fixation_data_list.append(df_selected)
        
        if i % 10 == 0:
            print(f"Processed {i}/{len(fixation_files)} fixation files")
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")

# Combine all fixation data (filter out None entries)
fixation_data_list = [df for df in fixation_data_list if df is not None]
if len(fixation_data_list) == 0:
    raise ValueError("No fixation data was successfully loaded. Please check your data files.")

fixation_data = pd.concat(fixation_data_list, ignore_index=True)
print(f"Total fixation records: {len(fixation_data)}")

# Save cleaned fixation data
fixation_data.to_csv("data/processed/fixation_cleaned.csv", index=False)
print("Saved fixation data to data/processed/fixation_cleaned.csv")

# %% Load Interest Area Reports
print("\nLoading interest area reports...")
interest_area_files = [f for f in Path(interest_area_dir).glob("*.xls")]
print(f"Found {len(interest_area_files)} interest area files")

interest_area_data_list = []

for i, file_path in enumerate(interest_area_files, 1):
    filename = file_path.name
    participant_id = extract_participant_id(filename)
    
    if participant_id is None:
        print(f"Warning: Could not extract participant ID from {filename}")
        continue
    
    try:
      
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-16-le', dtype=str, low_memory=False)
        except (UnicodeDecodeError, pd.errors.ParserError):
            # Fallback to Excel reader
            df = pd.read_excel(file_path, dtype=str, engine='xlrd')
        
        df['participant_id'] = participant_id
        df['data_file'] = filename
        
        # Select relevant variables from interest area reports
        relevant_vars = [
            # Participant and trial identifiers
            "participant_id", "data_file", "TRIAL_INDEX", "TRIAL_LABEL", "TRIAL_START_TIME",
            # Interest area metrics
            "IA_LABEL", "IA_DWELL_TIME", "IA_FIXATION_COUNT", "IA_FIRST_FIXATION_TIME",
            "IA_FIRST_FIXATION_DURATION", "IA_FIRST_FIXATION_INDEX",
            "IA_AREA", "IA_LEFT", "IA_RIGHT", "IA_TOP", "IA_BOTTOM",
            # Trial-level information
            "TRIAL_DWELL_TIME", "TRIAL_FIXATION_COUNT", "TRIAL_IA_COUNT",
            "sentence", "voice_id", "image_id", "stim_id", "image", "stimulus_file",
            "session_var", "exp_id", "language", "audio"
        ]
        
        vars_to_select = [v for v in relevant_vars if v in df.columns]
        df_selected = df[vars_to_select].copy()
        
        # Convert numeric columns
        numeric_cols = [
            "TRIAL_INDEX", "TRIAL_START_TIME", "IA_DWELL_TIME", "IA_FIXATION_COUNT",
            "IA_FIRST_FIXATION_TIME", "IA_FIRST_FIXATION_DURATION",
            "IA_FIRST_FIXATION_INDEX", "IA_AREA", "IA_LEFT", "IA_RIGHT",
            "IA_TOP", "IA_BOTTOM", "TRIAL_DWELL_TIME", "TRIAL_FIXATION_COUNT",
            "TRIAL_IA_COUNT"
        ]
        
        for col in numeric_cols:
            if col in df_selected.columns:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
        
        interest_area_data_list.append(df_selected)
        
        if i % 10 == 0:
            print(f"Processed {i}/{len(interest_area_files)} interest area files")
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")

# Combine all interest area data (filter out None entries)
interest_area_data_list = [df for df in interest_area_data_list if df is not None]
if len(interest_area_data_list) == 0:
    raise ValueError("No interest area data was successfully loaded. Please check your data files.")

interest_area_data = pd.concat(interest_area_data_list, ignore_index=True)
print(f"Total interest area records: {len(interest_area_data)}")

# Save cleaned interest area data
interest_area_data.to_csv("data/processed/interest_area_cleaned.csv", index=False)
print("Saved interest area data to data/processed/interest_area_cleaned.csv")

# %% Load Saccade Reports
print("\nLoading saccade reports...")
saccade_files = [f for f in Path(saccade_dir).glob("*.xls")]
print(f"Found {len(saccade_files)} saccade files")

saccade_data_list = []

for i, file_path in enumerate(saccade_files, 1):
    filename = file_path.name
    participant_id = extract_participant_id(filename)
    
    if participant_id is None:
        print(f"Warning: Could not extract participant ID from {filename}")
        continue
    
    try:
        # Read file - these are actually tab-separated UTF-16 files, not Excel
        # Try reading as UTF-16 tab-separated first, fall back to Excel if that fails
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-16-le', dtype=str, low_memory=False)
        except (UnicodeDecodeError, pd.errors.ParserError):
            # Fallback to Excel reader
            df = pd.read_excel(file_path, dtype=str, engine='xlrd')
        
        df['participant_id'] = participant_id
        df['data_file'] = filename
        
        # Select relevant variables from saccade reports
        relevant_vars = [
            # Participant and trial identifiers
            "participant_id", "data_file", "TRIAL_INDEX", "TRIAL_LABEL", "TRIAL_START_TIME",
            # Saccade metrics
            "CURRENT_SAC_DURATION", "CURRENT_SAC_AMPLITUDE", "CURRENT_SAC_AVG_VELOCITY",
            "CURRENT_SAC_PEAK_VELOCITY", "CURRENT_SAC_INDEX", "CURRENT_SAC_START_TIME",
            "CURRENT_SAC_END_TIME", "CURRENT_SAC_DIRECTION", "CURRENT_SAC_ANGLE",
            # Start and end positions
            "CURRENT_SAC_START_X", "CURRENT_SAC_START_Y", "CURRENT_SAC_END_X", "CURRENT_SAC_END_Y",
            # Interest area information
            "CURRENT_SAC_START_INTEREST_AREA_LABEL", "CURRENT_SAC_END_INTEREST_AREA_LABEL",
            "CURRENT_SAC_START_INTEREST_AREA_ID", "CURRENT_SAC_END_INTEREST_AREA_ID",
            # Trial-level information
            "sentence", "voice_id", "image_id", "stim_id", "image", "stimulus_file",
            "session_var", "exp_id", "language", "audio"
        ]
        
        vars_to_select = [v for v in relevant_vars if v in df.columns]
        df_selected = df[vars_to_select].copy()
        
        # Convert numeric columns
        numeric_cols = [
            "TRIAL_INDEX", "TRIAL_START_TIME", "CURRENT_SAC_DURATION",
            "CURRENT_SAC_AMPLITUDE", "CURRENT_SAC_AVG_VELOCITY", "CURRENT_SAC_PEAK_VELOCITY",
            "CURRENT_SAC_INDEX", "CURRENT_SAC_START_TIME", "CURRENT_SAC_END_TIME",
            "CURRENT_SAC_ANGLE", "CURRENT_SAC_START_X", "CURRENT_SAC_START_Y",
            "CURRENT_SAC_END_X", "CURRENT_SAC_END_Y", "CURRENT_SAC_START_INTEREST_AREA_ID",
            "CURRENT_SAC_END_INTEREST_AREA_ID"
        ]
        
        for col in numeric_cols:
            if col in df_selected.columns:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')
        
        saccade_data_list.append(df_selected)
        
        if i % 10 == 0:
            print(f"Processed {i}/{len(saccade_files)} saccade files")
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")

# Combine all saccade data (filter out None entries)
saccade_data_list = [df for df in saccade_data_list if df is not None]
if len(saccade_data_list) == 0:
    raise ValueError("No saccade data was successfully loaded. Please check your data files.")

saccade_data = pd.concat(saccade_data_list, ignore_index=True)
print(f"Total saccade records: {len(saccade_data)}")

# Save cleaned saccade data
saccade_data.to_csv("data/processed/saccade_cleaned.csv", index=False)
print("Saved saccade data to data/processed/saccade_cleaned.csv")

# %% Create participant metadata summary
all_participant_ids = pd.concat([
    pd.Series(fixation_data['participant_id'].unique()),
    pd.Series(interest_area_data['participant_id'].unique()),
    pd.Series(saccade_data['participant_id'].unique())
]).unique()

participant_metadata = pd.DataFrame({
    'participant_id': all_participant_ids
})

participant_metadata['has_fixation_data'] = participant_metadata['participant_id'].isin(
    fixation_data['participant_id'].unique()
)
participant_metadata['has_interest_area_data'] = participant_metadata['participant_id'].isin(
    interest_area_data['participant_id'].unique()
)
participant_metadata['has_saccade_data'] = participant_metadata['participant_id'].isin(
    saccade_data['participant_id'].unique()
)

participant_metadata.to_csv("data/processed/participant_metadata.csv", index=False)
print("\nSaved participant metadata to data/processed/participant_metadata.csv")

# %% Summary statistics
print("\n=== Data Loading Summary ===")
print(f"Participants: {len(participant_metadata)}")
print(f"Fixation records: {len(fixation_data)}")
print(f"Interest area records: {len(interest_area_data)}")
print(f"Saccade records: {len(saccade_data)}")
print("\nData loading complete!")

