import requests
from pprint import pprint
import configparser
from datetime import datetime

class EcoGuardClient:
    def __init__(self, username, password, domain):
        self.base_url = 'https://integration.ecoguard.se'
        self.username = username
        self.password = password
        self.domain = domain
        self.token = self.get_token()
        
    def get_token(self):
        url = f'{self.base_url}/token'
        payload = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'domain': self.domain,
            'issue_refresh_token': 'true'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise ConnectionError(f"Failed to get token: {response.status_code}")
        
    def make_request(self, method, endpoint, **kwargs):
        url = f'{self.base_url}/{endpoint}'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    def get_user_info(self):
        return self.make_request('GET', 'api/users/self?')
    
    def get_nodes_info(self, node_id):
        return self.make_request('GET', f'api/{self.domain}/nodes/{node_id}?')
    
    def get_node_data(self, node_id, interval='H', utl='ELEC[val]'):
        return self.make_request('GET', f'api/{self.domain}/data', params={
            'nodeID': node_id,
            'interval': interval,
            'utl': utl
        })

    def pretty_print_node_data(self, data):
        print("\nNode Data:")
        for node in data:
            node_id = node['ID']
            node_name = node['Name']
            print(f"\nNode ID: {node_id}, Node Name: {node_name}")
            for result in node['Result']:
                func = result['Func']
                unit = result['Unit']
                utl = result['Utl']
                print(f"  Func: {func}, Unit: {unit}, Utl: {utl}")
                print("  Values:")
                for value_entry in result['Values']:
                    timestamp = value_entry['Time']
                    value = value_entry['Value']
                    readable_time = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"    Time: {readable_time}, Value: {value}")

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
    
    node_data = client.get_node_data(node_id)
    print("\nNode Data:")
    pprint(node_data)
    client.pretty_print_node_data(node_data)

if __name__ == "__main__":
    main()