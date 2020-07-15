import os

from sqlalchemy import create_engine


os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


OracleConfig = {
    'host': '10.170.129.33',
    'port': 1521,
    'user': 'zgquery',
    'password': 'zgquery',
    'database': 'ZXDB',
    'db_engine': 'oracle'
}


MySQLConfig = {
    'host': '10.170.139.10',
    'port': 3306,
    'user': 'fund',
    'password': '123456',
    'database': 'fund_filter_django',
    'db_engine': 'mysql'
}


DATAYESConfig = {
    'host': '10.170.225.10',
    'port': 1521,
    'user': 'datayes',
    'password': 'datayes0108',
    'database': 'qtdatadb',
    'db_engine': 'oracle'
}


def enginemaker(user, password, host, port, database, db_engine):
    if db_engine == 'oracle':
        uri = f'oracle+cx_oracle://{user}:{password}@{host}:{port}/{database}'
    else:
        uri = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    return create_engine(uri)


oracle = enginemaker(**OracleConfig)
mysql = enginemaker(**MySQLConfig)
datayes = enginemaker(**DATAYESConfig)


__all__ = ['oracle', 'mysql', 'datayes']
