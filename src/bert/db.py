import os
import json
import psycopg2
import psycopg2.extras

def get_postgres_service():
    # Extract VCAP_SERVICES
    vcap_services_str = os.environ.get('VCAP_SERVICES')
    if vcap_services_str is None:
        raise Exception('VCAP_SERVICES environment variable not found.')
    vcap_services = json.loads(vcap_services_str)

    # Extract PostgreSQL service details
    return vcap_services['postgresql-db'][0]['credentials']

def connect_to_db():
    postgres_service = get_postgres_service()

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=postgres_service['hostname'],
        port=postgres_service['port'],
        user=postgres_service['username'],
        password=postgres_service['password'],
        dbname=postgres_service['dbname'],
    )
    return conn