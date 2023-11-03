import os
from pprint import pprint
import configparser
from datetime import datetime, timedelta
from ecoguard.ecoguard_client import EcoGuardClient
from ecoguard.utl_type import UtlType

def main():
    # Load Configurations
    config = configparser.ConfigParser()
    # Get the absolute path to the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config.read(os.path.join(script_dir, 'config.ini'))

    username = config['ECOGUARD']['USERNAME']
    password = config['ECOGUARD']['PASSWORD']
    domain = config['ECOGUARD']['DOMAIN']

    client = EcoGuardClient(username, password, domain)
    
    billings = client.get_billing_results()
    last_3_billings = billings

    for billing in last_3_billings:
        print(f"Billing Name: {billing['Billing']['Name']}")
        print(f"Start Date: {billing['Start']}")
        print(f"End Date: {billing['End']}")
        
        for part in billing.get('Parts', []):
            print(f"\nPart Name: {part['Name']}")
            
            for item in part.get('Items', []):
                print(f"    Quantity: {item['Quantity']} {item['QuantityUnit']}")
                print(f"    Total Cost: {item['TotalCostWithVAT']} SEK")
                print(f"    Rate : {item['RateWithVAT']} SEK")                
        print("\n" + "-"*50 + "\n")



if __name__ == "__main__":
    main()
