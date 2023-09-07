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
    A generator function that extracts the attribute names from the XML file.

    Args:
        root (xml.etree.ElementTree.Element): The root element of the XML file.

    Returns:
        set: A set of unique attribute names.
    """
    attribute_names = set()
    for port in root.iter():
        if port.tag in ["HFSamplingPort", "HFQueuingPort"]:
            attribute_names.update(port.attrib.keys())
    return attribute_names

def main(xml_files):
    """
    La fonction principale du script.

    Args:
        xml_files (list of str): Les chemins des fichiers XML à traiter.

    Returns:
        None
    """
    # Initialize an empty set to hold all attribute names from all files
    all_attribute_names = set()

    # Loop over each XML file
    for xml_file in xml_files:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Get the attribute names from the XML file
        attribute_names = extract_data(root)

        # Add the attribute names from this file to the overall set
        all_attribute_names.update(attribute_names)

    ordered_names=list(all_attribute_names)
    ordered_names.sort()
    # Print all unique attribute names
    for attribute_name in ordered_names:
        print(attribute_name)

if __name__ == "__main__":
    # Create the argument parser
    parser = argparse.ArgumentParser(description=extract_data.__doc__)
    parser.add_argument('xml_files', nargs='+', help='The paths to the XML files.')

    # Parse the arguments
    args = parser.parse_args()

    # Run the main function
    main(args.xml_files)


