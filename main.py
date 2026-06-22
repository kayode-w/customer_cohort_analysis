from db_conn import db_connection
import pandas as pd
from datetime import datetime, timedelta
from analytics import load_tables, generate_cohort, generate_retention_tbl, generate_cohort_table


engine = db_connection()

# testing the connection
conn_test = pd.read_sql(
    '''
    select tabl now onee_name FROM information_schema.tables WHERE table_schema = 'public'
    ''', engine
)
if len(conn_test) > 0:
    print(f'The schema contains {len(conn_test)} tables.\n')
    print(conn_test)

else:
    print('Connection successful but schema contains 0 tables.')


txn = load_tables('transactions')


