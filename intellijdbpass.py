import argparse
import csv
import getpass
from pykeepass import PyKeePass
from xml.etree import ElementTree as ET

def get_connection_uuid(datasources_xml_file, name):
    print(f"Reading Datasources XML file: {datasources_xml_file}")
    tree = ET.parse(datasources_xml_file)
    root = tree.getroot()
    for datasource in root.iter("data-source"):
        if(name == datasource.attrib["name"]):
            return datasource.attrib["uuid"]
    raise UnknownDatasourceName(name)

def get_password_from_keepass_db(keepass_file, password, uuid):
    db = PyKeePass(keepass_file, password=password)

    entry = db.find_entries_by_title(f"IntelliJ Platform DB — {uuid}", first=True)
    if(entry == None):
        raise UnknownKeepassEntry(uuid)
    return entry.password

def write_to_file(filename, data_dict):
    print(f"Writing to {filename}")
    fieldnames = ["connection","password"]
    with open(filename, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_dict)

def main():
    parser = argparse.ArgumentParser(description="This tool allows you to retrieve passwords from your IntelliJ database connections. " \
        " At this time, it only works if you are using Keepass to store your connection info (check your Intellij settings).")
    parser.add_argument("datasourcesXmlFile", help="The IntelliJ Datasources XML file")
    parser.add_argument("keepassFile", help="The Keepass file used to store Intellij DB password info")
    parser.add_argument("-c", "--connection", help="Retrieves the password for the single specified connection")
    parser.add_argument("-o", "--outputFile", help="Writes the results to a CSV file")
    args = parser.parse_args()

    keepass_file = args.keepassFile
    datasource_file = args.datasourcesXmlFile
    conn = args.connection

    password = getpass.getpass(prompt="Keepass DB Master PW:")

    uuid = get_connection_uuid(datasource_file, conn)

    conn_pw = get_password_from_keepass_db(keepass_file, password, uuid)

    print(f"\nPassword for connection {conn}: {conn_pw}")

    print("\nDONE")

class UnknownDatasourceName(Exception):
    def __init__(self, name):
        self.message = f"Could not find name: {name} in Datasources XML file"

class UnknownKeepassEntry(Exception):
    def __init__(self, uuid):
        self.message = f"Could not find a matching Keepass entry for uuid: {uuid}"

if __name__ == "__main__":
    main()