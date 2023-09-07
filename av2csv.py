import csv
import xml.etree.ElementTree as ET
import argparse
import os
import logging

logging.basicConfig(level=logging.INFO)

def get_all_files(directory):
    """
    Recursively get all files in a directory and its sub-directories.
    
    Args:
        directory (str): The path to the directory.
    
    Returns:
        list: A list of paths to all files in the directory and its sub-directories.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                logging.info(f'Found XML file: {file_path}')
                yield file_path

def parse_xml(file_path):
    tree = ET.parse(file_path)
    return tree.getroot()

def extract_data(root, attributes):
    for port in root.iter():
        if port.tag in ["HFSamplingPort", "HFQueuingPort"]:
            data = {attr: port.attrib.get(attr, '') for attr in attributes}
            yield data

def write_csv(base_name, file_name, data, file_path, attributes):
    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ['BaseName'] + attributes + ['FileName']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({**{'BaseName': base_name}, **data, **{'FileName': file_name} })


def main(xml_file, csv_file, filter_attributes):
    root = parse_xml(xml_file)
    data = extract_data(root, filter_attributes)
    if csv_file:
        for d in data:
            write_csv(os.path.basename(xml_file), xml_file, d, csv_file, filter_attributes)
    else:
        for d in data:
            print({**{'BaseName': os.path.basename(xml_file)}, **d, **{'FileName': xml_file}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract specified attributes from XML files.")
    parser.add_argument('-f', '--filter', required=True, help='The attributes to filter.', type=str)
    parser.add_argument('-o', '--output', help='The path to the output CSV file.')
    parser.add_argument('-d', '--directory', help='The path to a directory of XML files.')

    args = parser.parse_args()
    args.filter = args.filter.split(',')
    
    # Check if a directory was specified
    if args.directory:
        xml_files = list(get_all_files(args.directory))
    else:
        xml_files = args.xml_files

    # Initialize count for progress logging
    total_files = len(xml_files)
    current_file = 1

    if args.output:
        # If an output file was specified, write the headers to it
        with open(args.output, 'w', newline='') as csvfile:
            fieldnames = ['BaseName'] + args.filter + ['FileName']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    for xml_file in xml_files:
        logging.info(f'Processing file {current_file}/{total_files}: {xml_file}')
        current_file += 1
        main(xml_file, args.output, args.filter)
