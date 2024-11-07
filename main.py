import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from importlib.metadata import version, PackageNotFoundError

def check_requirements(requirements_file='requirements.txt'):
    """
    Check if all required packages are installed using importlib.metadata.

    Args:
        requirements_file (str): Path to requirements.txt file

    Returns:
        bool: True if all requirements are met, False otherwise
    """
    # Ensure requirements file exists
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found!")
        return False

    # Read requirements file
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    # Check each requirement
    missing_packages = []
    for requirement in requirements:
        # Parse package name and version
        if '>=' in requirement:
            package_name, required_version = requirement.split('>=')
        else:
            package_name = requirement
            required_version = None

        try:
            installed_version = version(package_name)
            if required_version and installed_version < required_version:
                print(f"Warning: {package_name} version {installed_version} is less than required version {required_version}")
                missing_packages.append(requirement)
        except PackageNotFoundError:
            missing_packages.append(requirement)

    if missing_packages:
        print("\nMissing or outdated required packages:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\nPlease install/update packages using:")
        print(f"pip install -r {requirements_file}")
        return False

    return True

def normalize_path(path):
    """Normalize file path to handle Windows paths correctly"""
    return os.path.normpath(path).replace('\\', '/')

def get_next_row_id(agg_df):
    """Get the next row ID number from the existing data"""
    existing_row_ids = agg_df['RowIDs'].unique()
    max_row_num = max([int(row_id.replace('Row', '')) for row_id in existing_row_ids])
    return max_row_num + 1

def get_column_mappings():
    """Define the exact mapping of columns to surveys and measures"""
    return {
        # SEL (3-5)
        2: {'survey': 'SEL (3-5)', 'measure': 'Rigorous Expectations'},

        # SEL (6-12)
        4: {'survey': 'SEL (6-12)', 'measure': 'Cultural Awareness and Action'},
        5: {'survey': 'SEL (6-12)', 'measure': 'Diversity and Inclusion'},
        6: {'survey': 'SEL (6-12)', 'measure': 'Rigorous Expectations'},

        # Fall 24 Student Competency Survey - Grades 3-5
        8: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Challenging Feelings'},
        9: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Learning Strategies'},
        10: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Positive Feelings'},
        11: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Self-Efficacy'},
        12: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Self-Management'},
        13: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Sense of Belonging'},
        14: {'survey': 'Fall 24 Student Competency Survey - Grades 3-5', 'measure': 'Supportive Relationships'},

        # Fall 24 Student Competency Survey - Grades 6-12
        16: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Challenging Feelings'},
        17: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Emotion Regulation'},
        18: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Positive Feelings'},
        19: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Self-Efficacy'},
        20: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Self-Management'},
        21: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Sense of Belonging'},
        22: {'survey': 'Fall 24 Student Competency Survey - Grades 6-12', 'measure': 'Social Awareness'}
    }

def combine_pano_data(district_file='district_aggregates_pano1.csv',
                      raw_file='VancouverSchoolDistrictAllDataLeadershipView07Nov2024.csv',
                      new_school_year=None,
                      new_year_gu=None,
                      output_path='combined_pano_data'):
    """
    Appends new measures from raw file to existing district aggregates data.
    Creates sequential RowIDs unique to each school/year combination.
    Uses exact column-to-survey mappings with preserved measure names.
    """

    # Normalize all file paths
    district_file = normalize_path(district_file)
    raw_file = normalize_path(raw_file)
    output_path = normalize_path(output_path)

    # Read district aggregates file
    agg_df = pd.read_csv(district_file)

    # Read raw file, skipping first row
    raw_df = pd.read_csv(raw_file, skiprows=[0])

    # Get column mappings
    column_mappings = get_column_mappings()

    # Get next available row number
    next_row_num = get_next_row_id(agg_df)

    # Initialize list for new rows
    new_rows = []

    # Track new school/year combinations
    new_row_assignments = {}

    # Process each school in raw file
    for idx, row in raw_df.iterrows():
        school_name = row['Name']
        year = new_school_year

        # Create unique key for this school/year combination
        combo_key = f"{school_name}_{year}"

        # Check if this is a new combination
        if combo_key not in new_row_assignments:
            new_row_assignments[combo_key] = f"Row{next_row_num}"
            next_row_num += 1

        # Get row ID for this combination
        row_id = new_row_assignments[combo_key]

        # Determine grade group
        if school_name in agg_df['Name'].unique():
            grade_group = agg_df[agg_df['Name'] == school_name]['Grade Group'].iloc[0]
        else:
            if 'Elementary' in school_name:
                grade_group = 'Elementary'
            elif 'Middle' in school_name:
                grade_group = 'Middle'
            else:
                grade_group = 'High'

        # Process each mapped column
        for col_idx, mapping in column_mappings.items():
            # Get the original column name from raw_df
            col_name = raw_df.columns[col_idx]
            value = row[col_name]

            # Convert numpy.float64 to percentage format
            if isinstance(value, (float, np.float64)):
                if np.isnan(value):
                    continue  # Skip empty values
                # Convert to percentage format (add decimal point)
                value = f".{int(float(value))}"
            elif not value:
                continue  # Skip empty values

            survey_type = mapping['survey']
            measure_name = mapping['measure']

            # Add row with exact measure name
            new_rows.append({
                'SCHOOL_YEAR': year,
                'YEAR_GU': new_year_gu,
                'Grade Group': grade_group,
                'Name': school_name,
                'Survey': survey_type,
                'Measure': measure_name,
                'Value': value,
                'RowIDs': row_id
            })

    # Convert new rows to DataFrame
    new_df = pd.DataFrame(new_rows)

    # Add Survey column to original data if it doesn't exist
    if 'Survey' not in agg_df.columns:
        agg_df.insert(agg_df.columns.get_loc('Measure'), 'Survey', '')

    # Combine original data with new rows
    combined_df = pd.concat([agg_df, new_df], ignore_index=True)

    # Generate date string in mmddyyyy format
    date_str = datetime.now().strftime('%m%d%Y')

    # Create final output path with date
    final_output_path = f"{output_path}_{date_str}.csv"

    # Create directory if it doesn't exist
    output_dir = os.path.dirname(final_output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Print summary of changes
    print(f"Original number of rows: {len(agg_df)}")
    print(f"New rows added: {len(new_df)}")
    print(f"Total rows in combined dataset: {len(combined_df)}")
    print("\nMeasures by grade group and survey type:")
    for grade in sorted(new_df['Grade Group'].unique()):
        grade_data = new_df[new_df['Grade Group'] == grade]
        print(f"\n{grade}:")
        for survey in sorted(grade_data['Survey'].unique()):
            measures = grade_data[grade_data['Survey'] == survey]['Measure'].unique()
            print(f"  {survey}:")
            for measure in sorted(measures):
                print(f"    - {measure}")
    print(f"\nSaving combined data to: {final_output_path}")

    # Save the combined data
    combined_df.to_csv(final_output_path, index=False)

    return combined_df

# Import configuration
try:
    import config
except ImportError:
    print("Error: config.py not found! Please ensure config.py is in the same directory.")
    sys.exit(1)

# At the bottom of the file:
if __name__ == "__main__":
    # Check requirements first
    if not check_requirements():
        sys.exit(1)

    try:
        # If requirements are met, proceed with the script
        combined_data = combine_pano_data(
            district_file=config.DISTRICT_FILE,
            raw_file=config.RAW_FILE,
            new_school_year=config.NEW_SCHOOL_YEAR,
            new_year_gu=config.NEW_YEAR_GU,
            output_path=config.OUTPUT_PATH
        )
    except Exception as e:
        print(f"\nError running script: {str(e)}")
        print("\nPlease check your input files and configuration settings.")
        sys.exit(1)