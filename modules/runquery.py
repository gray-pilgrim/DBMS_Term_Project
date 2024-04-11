from configparser import ConfigParser
import psycopg2

auto_commit = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT

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

def connect(config,dbname):
    global auto_commit
    try:
        # trying to connect to database
        conn = psycopg2.connect (
            host = config['host'],
            port = config['port'],
            dbname = dbname,
            user = config['user'],
            password = config['password']
        )
        conn.set_isolation_level(auto_commit)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        exit(0)

    cur = conn.cursor()
    return cur, conn

def runQuery(query,dbname):
    config = load_config('database.ini', 'postgresql')
    cursor, conn = connect(config,dbname)

    try:
        cursor.execute(query=query)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return

    value = None
    try:
        value = cursor.fetchall()
    except:
        pass

    conn.commit()
    cursor.close()
    conn.close()

    return value