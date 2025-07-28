import os
from sqlalchemy import create_engine
import pandas as pd

# 1. Create SQL Server engine using Windows Authentication
def create_sql_server_engine(server, database, driver='ODBC+Driver+17+for+SQL+Server'):
    connection_string = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"
    engine = create_engine(connection_string)
    return engine

# 2. Query any SQL statement
def query_db(engine, sql_string):
    df = pd.read_sql(sql=sql_string, con=engine)
    return df

# 3. Save dataframe to table
def save_table(df, table_name, mode, engine):
    if mode not in ['replace', 'append']:
        raise ValueError("Mode must be 'replace' or 'append'")
    df.to_sql(name=table_name, con=engine, if_exists=mode, index=False)
    print(f"Saved {len(df)} rows to table '{table_name}' in mode '{mode}'")

