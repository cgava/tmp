import csv
import xml.etree.ElementTree as ET
import argparse

def parse_xml(file_path):
    """
    Parse le fichier XML.
    
    Args:
        file_path (str): Le chemin du fichier XML à analyser.

    Returns:
        ElementTree.Element: La racine de l'arbre XML.
    """
    tree = ET.parse(file_path)
    return tree.getroot()

def extract_data(root):
    """
    A generator function that extracts the desired data from the XML file.

    Args:
        root (xml.etree.ElementTree.Element): The root element of the XML file.

    Yields:
        A dictionary containing the desired data.
    """
    #ns = {'ate': 'http://fr.alyotech.ate/ATE/'}
    for bus in root.iter('bus'):
        for channel in bus.iter('channels'):
            for dataContainer in channel.iter('dataContainers'):
                parent_name = dataContainer.attrib['name']
                for attr in dataContainer.iter('attributes'):
                    if attr.attrib['name'] == 'Direction':
                        direction = attr.attrib['value']
                        break
                for sublist in dataContainer.iter('sublists'):
                    sublist_type = sublist.attrib['type']
                    if sublist_type in ["AFDX+Sampling Port", "AFDX+Queuing Port", "AFDX+SAP Port"]:
                        sublist_name = sublist.attrib['name']
                        guid = sublist.find('configs').attrib['value']
                        rate = None
                        for attr in sublist.iter('attributes'):
                            if attr.attrib['name'] == 'Rate (ms)':
                                rate = attr.attrib['value']
                                break
                        yield {'Name': sublist_name, 'VLDirection': direction ,'GUID': guid, 'Rate (ms)': rate, 'Parent DataContainer': parent_name}

if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description=extract_data.__doc__)
    parser.add_argument('xml_files', nargs='+', help='The paths to the XML files.')
    parser.add_argument('-o', '--output', help='The path to the output CSV file.')

    # Parse the arguments
    args = parser.parse_args()

    # Initialize an empty list to hold all data from all files
    all_data = []

    # Loop over each XML file
    for xml_file in args.xml_files:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Get the data from the XML file
        data = extract_data(root)

        # Add the data from this file to the overall data
        all_data.extend(data)

    if args.output:
        # If an output file was specified, write the data to it
        with open(args.output, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'VLDirection', 'GUID', 'Rate (ms)', 'Parent DataContainer']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)
    else:
        # Otherwise, print the data to the console
        for row in all_data:
            print(row)

