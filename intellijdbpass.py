import argparse
import csv
import getpass
from pykeepass import PyKeePass
from xml.etree import ElementTree as ET

header_columns = ["Connection","JDBC URL","Username","Password"]

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

def get_usernames_from_datasources_local_file(datasources_local_xml_file):
    """
    This gets ALL of the usernames from the datasources-local.xml file, in a map with the name being the key.
    This is needed because sometimes the datasources.xml file doesn't have the usernames.
    """
    print(f"Reading Datasources Local XML file: {datasources_local_xml_file}")
    tree = ET.parse(datasources_local_xml_file)
    root = tree.getroot()
    component = root.find("component")
    output = {}
    for datasource in component.iter("data-source"):
        username_elem = datasource.find("user-name")
        user_name = username_elem.text
        output[datasource.attrib["name"]] = user_name
    return output

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
    parser.add_argument("-u", "--usernameFile", help="The Datasources.Local.XML file. Use this if the Datasources.xml file does not contain the usernames (which may or may not be the case)")
    args = parser.parse_args()

    keepass_file = args.keepassFile
    datasource_file = args.datasourcesXmlFile
    conn_name = args.connection
    get_all_conns = args.allConnections if args.allConnections != None else False
    output_file = args.outputFile
    username_file = args.usernameFile

    password = getpass.getpass(prompt="Keepass DB Master PW:")

    uuid_dict = get_connection_info(datasource_file)
    username_dict = None if username_file == None else get_usernames_from_datasources_local_file(username_file)

    if get_all_conns == False:
        print(f"\nGetting connection info for connection: {conn_name}")
        single_conn = get_connection_single(uuid_dict, conn_name)
        uuid = single_conn["UUID"]
        jdbc_url = single_conn["JDBC URL"]
        conn_user, conn_pw = get_password_from_keepass_db(keepass_file, password, uuid)
        if(conn_user == None and username_dict != None):
            conn_user = username_dict[conn_name]
        print(f"\nPassword for connection {conn_name}: user: {conn_user}, pass: {conn_pw}")
        data_dict_list = [{"Connection":conn_name, "JDBC URL":jdbc_url, "Username":conn_user, "Password":conn_pw}]
    else:
        print("Getting all connections")
        get_all_passwords_from_keepass_db(keepass_file, password, uuid_dict)
        data_dict_list = uuid_dict

        # Fill in the usernames if they weren't in the datasources or the password files
        if username_dict != None:
            for temp_dict in data_dict_list:
                user = temp_dict["Username"]
                if(user == None):
                    conn_name = temp_dict["Connection"]
                    user = username_dict[conn_name]
                    temp_dict["Username"] = user

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