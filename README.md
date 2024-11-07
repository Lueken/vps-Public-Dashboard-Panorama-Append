# Panorama Data Processing Script

This script processes Panorama survey data and combines it with previous district aggregates for the VPS Public Dashboard.

## Prerequisites

- Python 3.8 or higher
- Required Python packages (installed automatically via requirements.txt)

## Installation

1. Clone or download this repository
2. Open a terminal/command prompt
3. Navigate to the script directory
4. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
5. Activate the virtual environment:
    - Windows:
      ```bash
      venv\Scripts\activate
      ```
    - Mac/Linux:
      ```bash
      source venv/bin/activate
      ```
6. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your input files in the same directory:
    - district_aggregates_pano1.csv
    - VancouverSchoolDistrictAllDataLeadershipView07Nov2024.csv

2. Run the script:
   ```bash
   python main.py
   ```

3. The script will:
    - Check for required dependencies
    - Process the data
    - Create a new combined file with today's date in the filename

## Configuration

Edit these values in the script to account for new school year data and output:
- new_school_year
- new_year_gu
- output_path

## Output

The script will create a new CSV file named:
- combined_pano_data_MMDDYYYY.csv (where MMDDYYYY is today's date)