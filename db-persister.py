import configparser
import psycopg2
import os
from datetime import datetime, timedelta
from ecoguard.ecoguard_client import EcoGuardClient
from ecoguard.utl_type import UtlType
from pprint import pprint

def get_latest_timestamp(cursor, utl_type):
    """
    Fetch the latest timestamp for a specific utl_type from the database.
    """
    cursor.execute("SELECT MAX(timestamp) FROM node_data WHERE utl = %s;", (utl_type,))
    result = cursor.fetchone()
    return result[0] if result[0] is not None else None

def insert_data_to_db(cursor, node, func, unit, utl, timestamp, value):
    insert_query = """
    INSERT INTO node_data (node_id, node_name, func, unit, utl, timestamp, value)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT ON CONSTRAINT idx_unique_node_data
    DO UPDATE SET value = EXCLUDED.value;
    """
    cursor.execute(insert_query, (node['ID'], node['Name'], func, unit, utl, timestamp, value))

def main():
    # Load Configurations
    config = configparser.ConfigParser()
    # Get the absolute path to the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config.read(os.path.join(script_dir, 'config.ini'))


    # EcoGuard API configurations
    ecoguard_username = config['ECOGUARD']['USERNAME']
    ecoguard_password = config['ECOGUARD']['PASSWORD']
    ecoguard_domain = config['ECOGUARD']['DOMAIN']
    
    # PostgreSQL configurations
    db_host = config['POSTGRES']['HOST']
    db_name = config['POSTGRES']['DATABASE']
    db_user = config['POSTGRES']['USER']
    db_password = config['POSTGRES']['PASSWORD']

    # Initialize EcoGuardClient
    client = EcoGuardClient(ecoguard_username, ecoguard_password, ecoguard_domain)
    
    print("Starting database persisting!")

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
    cursor = conn.cursor()
    
    try:
        # Fetch data from EcoGuard API
        user_info = client.get_user_info()
        node_id = user_info.get('NodeID')

        # Assume UtlType is an Enum with your types
        for utl_type in UtlType:
            latest_timestamp = get_latest_timestamp(cursor, utl_type.code)
            
            if latest_timestamp:
                from_datetime = latest_timestamp
            elif utl_type is UtlType.TEMPERATURE:
                print(f"Initial loading for {utl_type.name}, loading from one year ago")
                from_datetime = datetime.now() - timedelta(days=365)
            else:
                print(f"Initial loading for {utl_type.name}, loading from start")
                from_datetime = None

            try:
                node_data = client.get_node_data(node_id, utl_type, from_datetime)
                pprint(node_data)
                for node in node_data:
                    for result in node['Result']:
                        func = result['Func']
                        unit = result['Unit']
                        utl = result['Utl']
                        for value_entry in result['Values']:
                            timestamp = value_entry['Time']
                            value = value_entry['Value']
                            insert_data_to_db(cursor, node, func, unit, utl, timestamp, value)
                
                # Commit database transaction
                conn.commit()
                
            except Exception as e:
                print(f"Failed to fetch or insert data for {utl_type.name}: {str(e)}")
                conn.rollback()  # Revert changes on error
    finally:
        # Close database connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
