import os
import psycopg2
import configparser
from ecoguard.ecoguard_client import EcoGuardClient

def insert_billing_to_db(cursor, billing):
    insert_query = """
    INSERT INTO billing_data (billing_name, start_date, end_date, part_name, quantity, quantity_unit, total_cost_with_vat, rate_with_vat)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING;
    """
    billing_name = billing['Billing']['Name']
    start_date = billing['Start']
    end_date = billing['End']
    
    for part in billing.get('Parts', []):
        part_name = part['Name']
        
        for item in part.get('Items', []):
            quantity = item['Quantity']
            quantity_unit = item['QuantityUnit']
            total_cost_with_vat = item['TotalCostWithVAT']
            rate_with_vat = item['RateWithVAT']
            
            cursor.execute(insert_query, (billing_name, start_date, end_date, part_name, quantity, quantity_unit, total_cost_with_vat, rate_with_vat))

def main():
    # Load Configurations
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config.read(os.path.join(script_dir, 'config.ini'))

    username = config['ECOGUARD']['USERNAME']
    password = config['ECOGUARD']['PASSWORD']
    domain = config['ECOGUARD']['DOMAIN']
    db_host = config['POSTGRES']['HOST']
    db_name = config['POSTGRES']['DATABASE']
    db_user = config['POSTGRES']['USER']
    db_password = config['POSTGRES']['PASSWORD']

    client = EcoGuardClient(username, password, domain)
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
    cursor = conn.cursor()

    try:
        billings = client.get_billing_results()
        
        for billing in billings:
            insert_billing_to_db(cursor, billing)
            
        # Commit database transaction
        conn.commit()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Revert changes on error
    finally:
        # Close database connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()