#!/usr/bin/env python3
"""
Main script to run the eye-tracking analysis pipeline
Run all scripts in sequence
"""

import sys
import subprocess
import os
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent
os.chdir(script_dir.parent)

scripts = [
    "scripts/01_load_and_clean_data.py",
    "scripts/02_create_analysis_variables.py",
    "scripts/03_merge_datasets.py",
    "scripts/04_data_quality.py",
    "scripts/05_exploratory_analysis.py",
]

def run_script(script_path):
    """Run a Python script and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {script_path}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False
        )
        print(f"\n[OK] Completed: {script_path}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error in {script_path}")
        print(f"Exit code: {e.returncode}\n")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to run {script_path}: {str(e)}\n")
        return False

def main():
    """Run all analysis scripts in sequence."""
    print("Starting Eye-Tracking Analysis Pipeline...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}\n")
    
    for script in scripts:
        if not Path(script).exists():
            print(f"Warning: Script {script} not found, skipping...")
            continue
        
        success = run_script(script)
        if not success:
            print(f"\nPipeline stopped due to error in {script}")
            print("Please fix the error and try again.")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("Pipeline completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()

