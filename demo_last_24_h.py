import requests
from pprint import pprint
import configparser
from datetime import datetime, timedelta
from ecoguard.ecoguard_client import EcoGuardClient
from ecoguard.utl_type import UtlType

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    username = config['ECOGUARD']['USERNAME']
    password = config['ECOGUARD']['PASSWORD']
    domain = config['ECOGUARD']['DOMAIN']

    client = EcoGuardClient(username, password, domain)
    user_info = client.get_user_info()
    print("User Info:")
    pprint(user_info)
    
    node_id = user_info.get('NodeID')
    nodes_info = client.get_nodes_info(node_id)
    print("\nNodes Info:")
    pprint(nodes_info)
    
    # Getting data for the last 24 hours
    from_datetime = datetime.utcnow() - timedelta(days=1)
    to_datetime = datetime.utcnow()    
    for utl_type in UtlType:
        print(f"\nFetching data for: {utl_type.name}")
        try:
            node_data = client.get_node_data(node_id, utl_type, from_datetime, to_datetime)
            client.pretty_print_node_data(node_data)
        except Exception as e:
            print(f"Failed to fetch or print data for {utl_type.name}: {str(e)}")

if __name__ == "__main__":
    main()
