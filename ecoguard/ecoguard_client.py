import requests
from pprint import pprint
from datetime import datetime
from ecoguard.utl_type import UtlType

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
            print(f"Error: {response.status_code}")
            print("Response data:")
            pprint(response.text)
            response.raise_for_status()

    def get_user_info(self):
        return self.make_request('GET', 'api/users/self?')
    
    def get_nodes_info(self, node_id):
        return self.make_request('GET', f'api/{self.domain}/nodes/{node_id}?')
    
    def get_node_data(self, node_id, utl, from_datetime=None, to_datetime=None, interval='H'):
        if from_datetime:
            from_timestamp = int(from_datetime.replace(minute=0, second=0).timestamp())
        else:
            from_timestamp = None

        if to_datetime:
            to_timestamp = int(to_datetime.replace(minute=0, second=0).timestamp())
        else:
            to_timestamp = None

        response_data = self.make_request('GET', f'api/{self.domain}/data', params={
            'nodeID': node_id,
            'interval': interval,
            'utl': f"{utl.value}",
            'from': from_timestamp,
            'to': to_timestamp
        })

        for node in response_data:
            for result in node['Result']:
                for value_entry in result['Values']:
                    value_entry['Value'] = round(float(value_entry['Value']), 3)

        return response_data
    
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