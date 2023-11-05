import os
from sqlalchemy import create_engine
from sqlalchemy import text
import pymysql
pymysql.install_as_MySQLdb()


def get_connection_string():
    user = os.environ.get('COLLECTOR_DB_USER')
    password = os.environ.get('COLLECTOR_DB_PASS')
    host = os.environ.get('COLLECTOR_DB_HOST')
    port = os.environ.get('COLLECTOR_DB_PORT')
    database = os.environ.get('COLLECTOR_DB_NAME')
    return f'mysql://{user}:{password}@{host}:{port}/{database}'


def get_connection():
    engine = create_engine(get_connection_string(), echo=True)
    return engine.connect()


def exists_by(conn, table, field, value):
    exists = False
    query = text(f"SELECT count(*) FROM {table} WHERE {field}='{value}'")
    try:
        result = conn.execute(query)
        for row in result:
            exists = row[0] > 0
    except Exception as e:
        print(f'Error: {e}')

    return exists


def save_url_process(conn, url):
    cod = url.split('/')[-1]
    if not exists_by(conn, 'complaints_process', 'ra_cod', cod):
        query = text(f"INSERT INTO complaints_process (ra_cod, link, status) VALUES('{cod}', '{url}', 'pending')")
        try:
            conn.execute(query)
            conn.commit()
        except Exception as e:
            print(f'Error: {e}')


def save_urls(conn, urls):
    for url in urls:
        save_url_process(conn, url)


def get_last_id(conn, table):
    last_id = 1
    query = text(f"SELECT max(id) last_id FROM {table}")
    try:
        result = conn.execute(query)
        for row in result:
            last_id = row[0]
        return last_id
    except Exception as e:
        print(f'Error: {e}')
        return last_id


def create_complainer(conn, complainer):
    query = text(f"""
        INSERT INTO complainers
        (cpf, name, uc, city, email, phone, is_client)
        VALUES('{complainer.cpf}', '{complainer.name}', '{complainer.uc}',
         '{complainer.city}', '{complainer.email}', '{complainer.phone}', '{complainer.is_client}')""")
    try:
        conn.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False


def create_complaint(conn, complaint, complainer_id):
    query = text(f"""
        INSERT INTO complaints
        (ra_cod, ra_id, title, date_description, chanel, reason, description, complainer_id)
        VALUES('{complaint.cod}',
         '{complaint.identifier}',
         '{complaint.title}',
         '{complaint.date}',
          '{complaint.chanel}',
          '{complaint.reason}',
          '{complaint.description}',
           {complainer_id})""")
    try:
        conn.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False


def register_complaint(conn, complaint):
    if create_complainer(conn, complaint.complainer):
        return create_complaint(conn, complaint, get_last_id(conn, 'complainers'))
    return False


def done_complaint_process(conn, cod):
    query = text(f"UPDATE complaints_process SET status='done' WHERE ra_cod='{cod}'")
    try:
        conn.execute(query)
        conn.commit()
    except Exception as e:
        print(f'Error: {e}')


def get_pending_urls(conn):
    urls = []
    query = text(f"SELECT link FROM complaints_process WHERE status = 'pending'")
    try:
        result = conn.execute(query)
        for row in result:
            urls.append(row[0])
    except Exception as e:
        print(f'Error: {e}')
    return urls


def get_processed(conn):
    urls = []
    query = text(f"SELECT link FROM complaints_process WHERE status = 'ok'")
    try:
        result = conn.execute(query)
        for row in result:
            urls.append(row[0])
    except Exception as e:
        print(f'Error: {e}')
    return urls
