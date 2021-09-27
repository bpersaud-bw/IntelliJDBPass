import argparse
import csv
import getpass
from pykeepass import PyKeePass
from xml.etree import ElementTree as ET

header_columns = ["Connection","JDBC URL","Username","Password"]

# def get_connection_uuid(datasources_xml_file, name):
#     """
#     This gets the UUID for a given connection name
#     """
#     print(f"Reading Datasources XML file: {datasources_xml_file}")
#     tree = ET.parse(datasources_xml_file)
#     root = tree.getroot()
#     for datasource in root.iter("data-source"):
#         if(name == datasource.attrib["name"]):
#             return datasource.attrib["uuid"]
#     raise UnknownDatasourceName(name)

def get_connection_info(datasources_xml_file):
    """
    This gets ALL of the UUIDs for all the connections
    """
    print(f"Reading Datasources XML file: {datasources_xml_file}")
    tree = ET.parse(datasources_xml_file)
    root = tree.getroot()
    output = []
    for datasource in root.iter("data-source"):
        jdbc_url = get_jdbc_url(datasource)
        output.append({"Connection":datasource.attrib["name"], "UUID":datasource.attrib["uuid"], "JDBC URL":jdbc_url})
    return output

def get_connection_single(connections, name):
    for temp_conn in connections:
        if(temp_conn["Connection"] == name):
            return temp_conn
    raise UnknownDatasourceName(name)

def get_jdbc_url(datasource_elem):
    jdbc_url_elem = datasource_elem.find("jdbc-url")
    jdbc_url = jdbc_url_elem.text if jdbc_url_elem != None else ""
    return jdbc_url

def get_all_passwords_from_keepass_db(keepass_file, keepass_file_password, conn_dict_list):
    """
    Augments the incoming connection dictionary with the passwords
    """
    db = PyKeePass(keepass_file, password=keepass_file_password)

    for conn_dict in conn_dict_list:
        entry = db.find_entries_by_title(f"IntelliJ Platform DB — {conn_dict['UUID']}", first=True)
        conn_dict["Username"] = entry.username if entry != None else ""
        conn_dict["Password"] = entry.password if entry != None else ""

def get_password_from_keepass_db(keepass_file, keepass_file_password, uuid):
    db = PyKeePass(keepass_file, password=keepass_file_password)

    entry = db.find_entries_by_title(f"IntelliJ Platform DB — {uuid}", first=True)
    if(entry == None):
        raise UnknownKeepassEntry(uuid)
    return (entry.username, entry.password)

def write_to_file(filename, data_dict_list):
    print(f"\nWriting to {filename}")
    with open(filename, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=header_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data_dict_list)

def main():
    parser = argparse.ArgumentParser(description="This tool allows you to retrieve passwords from your IntelliJ database connections. " \
        " At this time, it only works if you are using Keepass to store your connection info (check your Intellij settings).")
    parser.add_argument("datasourcesXmlFile", help="The IntelliJ Datasources XML file; has your Connection info")
    parser.add_argument("keepassFile", help="The Keepass filethat has your Passwords")
    parser.add_argument("-c", "--connection", help="Retrieves the password for the single specified connection")
    parser.add_argument("-a", "--allConnections", help="Get all the connections instead of just a single one", action="store_true")
    parser.add_argument("-o", "--outputFile", help="Writes the results to a CSV file")
    args = parser.parse_args()

    keepass_file = args.keepassFile
    datasource_file = args.datasourcesXmlFile
    conn_name = args.connection
    get_all_conns = args.allConnections if args.allConnections != None else False
    output_file = args.outputFile

    password = getpass.getpass(prompt="Keepass DB Master PW:")

    uuid_dict = get_connection_info(datasource_file)
    if get_all_conns == False:
        print(f"\nGetting connection info for connection: {conn_name}")
        # uuid = get_connection_uuid(datasource_file, conn)
        single_conn = get_connection_single(uuid_dict, conn_name)
        uuid = single_conn["UUID"]
        jdbc_url = single_conn["JDBC URL"]
        conn_user, conn_pw = get_password_from_keepass_db(keepass_file, password, uuid)
        print(f"\nPassword for connection {conn_name}: user: {conn_user}, pass: {conn_pw}")
        data_dict_list = [{"Connection":conn_name, "JDBC URL":jdbc_url, "Username":conn_user, "Password":conn_pw}]
    else:
        print("Getting all connections")
        get_all_passwords_from_keepass_db(keepass_file, password, uuid_dict)
        data_dict_list = uuid_dict
        if(output_file == None):
            print("Passwords (Consider sending passwords to file instead...):")
            for temp_dict in data_dict_list:
                conn_name = temp_dict["Connection"]
                user = temp_dict["Username"]
                pw = temp_dict["Password"]
                print(f"\tConnection {conn_name}: user: {user}, pw: {pw}")

    if(output_file != None):
        write_to_file(output_file, data_dict_list)

    print("\nDONE")

class UnknownDatasourceName(Exception):
    def __init__(self, name):
        self.message = f"Could not find name: {name} in Datasources XML file"

class UnknownKeepassEntry(Exception):
    def __init__(self, uuid):
        self.message = f"Could not find a matching Keepass entry for UUID: {uuid}"

if __name__ == "__main__":
    main()