import pandas as pd
import numpy as np
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_csv(utest_file, av_file, output_file, stop_after_merge=False):
    '''
    This function takes two CSV files, merges them based on a common column, and creates new columns based on specified conditions.
    The final DataFrame is either written into a new CSV file or printed to the console.

    Parameters:
    utest_file (str): The path to the first CSV file.
    av_file (str): The path to the second CSV file.
    output_file (str, optional): The path to the output CSV file. If None, the result is printed to the console.
    stop_after_av (bool, optional): If True, the script stops after processing the av_file and writes the result into the output_file.

    Returns:
    None
    '''

    # Load data
    utest = pd.read_csv(utest_file)
    av = pd.read_csv(av_file)
    
    # Add new column 'isRateNull'
    utest['isRateNull'] = utest['Rate (ms)'].apply(lambda x: 'true' if x == 0.0 else '_')

    # Create dictionary for GuidDef with non-null values, indexed by Guid
    class_dict = av[av['GuidDef'].isnull()].set_index('Guid')[['Direction', 'SamplePeriod', 'RefreshPeriod']].to_dict('index')

    # Iterate through the rows in av with non-null GuidDef
    for _, instance in av[av['GuidDef'].notnull()].iterrows():
        if instance['GuidDef'] in class_dict:
            # Save original values for logging
            original_values = av.loc[av['GuidDef'] == instance['GuidDef'], ['Direction', 'SamplePeriod', 'RefreshPeriod']].values[0]

            # Update rows where GuidDef equals Guid of the current row with values from class_dict
            av.loc[av['GuidDef'] == instance['GuidDef'], ['Direction', 'SamplePeriod', 'RefreshPeriod']] = list(class_dict[instance['GuidDef']].values())

            # Log the changes
            logging.info(f"Updated row for GuidDef {instance['GuidDef']}:")
            logging.info(f"Before: Direction = {original_values[0]}, SamplePeriod = {original_values[1]}, RefreshPeriod = {original_values[2]}")
            logging.info(f"After: Direction = {class_dict[instance['GuidDef']]['Direction']}, SamplePeriod = {class_dict[instance['GuidDef']]['SamplePeriod']}, RefreshPeriod = {class_dict[instance['GuidDef']]['RefreshPeriod']}")

    if stop_after_merge:
        if output_file:
            av.to_csv(output_file, index=False)
        else:
            print(av)
        return

    # Merge the two DataFrames based on the GUID/Guid column, keep all rows from 'utest' (left join)
    merged = pd.merge(utest, av, left_on='GUID', right_on='Guid', how='left')

    # Replace NaN values in specified columns with 'Not Found'
    merged[['FileName', 'Direction', 'SamplePeriod', 'RefreshPeriod']] = merged[['FileName', 'Direction', 'SamplePeriod', 'RefreshPeriod']].fillna('Not Found')

    # Create new columns based on specified conditions
    merged['isSample'] = np.where(merged['Rate (ms)'] == merged['SamplePeriod'], 'true', '')
    merged['isRefresh'] = np.where(merged['Rate (ms)'] == merged['RefreshPeriod'], 'true', '')
    merged['Bilan'] = np.where((merged['isSample'] == 'true') | (merged['isRefresh'] == 'true'), 'OK', 'KO')

    # Write the final DataFrame into a new CSV file or print to console
    if output_file:
        merged.to_csv(output_file, index=False)
    else:
        print(merged)

if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("utest_file", help="The path to the first CSV file.")
    parser.add_argument("av_file", help="The path to the second CSV file.")
    parser.add_argument("-o", "--output", help="The path to the output CSV file. If not provided, the result is printed to the console.")
    parser.add_argument("-s", "--stop", action='store_true', help="If set, the script stops after processing the av_file and writes the result into the output_file.")

    # Parse command line arguments
    args = parser.parse_args()

    # Run the function with the provided arguments
    process_csv(args.utest_file, args.av_file, args.output, args.stop)
