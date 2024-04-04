from configparser import ConfigParser
import psycopg2


def load_config(filename, section):
    parser = ConfigParser()
    parser.read(filename)

    # get section
    # initiate a dict
    config = {}
    # checking if section is present
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config

def connect(config):
    try:
        # trying to connect to database
        conn = psycopg2.connect (
            host = config['host'],
            port = config['port'],
            dbname = config['database'],
            user = config['user'],
            password = config['password']
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        exit(0)

    cur = conn.cursor()
    return cur, conn

def runQuery(query, database = 'user_database_list'):
    if(database == 'user_database_list'):
        config = load_config('database.ini', 'postgresql')
    else:
        config = load_config('database.ini', 'other')
        config['database'] = database

    cursor, conn = connect(config)

    try:
        cursor.execute(query=query)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return error

    value = None
    try:
        value = cursor.fetchall()
    except:
        pass

    conn.commit()
    cursor.close()
    conn.close()

    return value
