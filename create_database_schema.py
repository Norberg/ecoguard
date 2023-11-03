import os
import configparser
import psycopg2

def execute_sql_file(conn, sql_file_path):
    cursor = conn.cursor()
    
    with open(sql_file_path, 'r') as sql_file:
        sql_queries = sql_file.read()
    
    try:
        cursor.execute(sql_queries)
        conn.commit()
    except Exception as e:
        print(f"An error occurred while executing the SQL file: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    # Load Configurations
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config.read(os.path.join(script_dir, 'config.ini'))

    db_host = config['POSTGRES']['HOST']
    db_name = config['POSTGRES']['DATABASE']
    db_user = config['POSTGRES']['USER']
    db_password = config['POSTGRES']['PASSWORD']

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host
    )
    
    sql_file_path = os.path.join(script_dir, 'schema.sql')
    
    execute_sql_file(conn, sql_file_path)
    
    conn.close()

if __name__ == "__main__":
    main()