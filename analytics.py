from db_conn import db_connection
import pandas as pd 
from datetime import datetime, timedelta

engine = db_connection()

# Fist function for loading the tables in, we could choose to pass in a single table or a list of tables and store in a dict. 
def load_tables(tbl_name: str | list) -> pd.DataFrame:
    """
        Takes a table name or list of table names and loads them from the database.

        Parameters:
            tbl_name — str or list: a single table name or a list of table names to load

        Returns:
            A single pandas DataFrame if a string is passed, or a dictionary of 
            DataFrames if a list is passed — where each key is the table name and 
            the value is the corresponding DataFrame.
    """
    #If the params passed is a string, let's load the table in natively
    if isinstance(tbl_name, str):
        try:
            query = pd.read_sql(f'select * from {tbl_name}', engine)
            return query
        except Exception as e:
            raise ValueError(f"Error loading table {tbl_name}: {e}") # if there's an error, we raise a ValueError with a descriptive message
       
    # If a list is passed, we loop through the list and load each table, returning a dictionary of DataFrames
    elif isinstance(tbl_name, list):
        try:
            tables = {}
            for tbl in tbl_name:
                query = pd.read_sql(f'select * from {tbl}', engine)
                tables[tbl] = query #asigning the query result to the corresponding table name in the tables dictionary
            return tables    
           
        except Exception as e:
            raise ValueError(f"Error loading table: {tbl}: {e}")

    else:
        raise TypeError("tbl_name must be a string or a list of strings.")

    
# Next step, we need to create our base cohort and size
def generate_cohort(df: pd.DataFrame) -> pd.DataFrame:
    try:

        df['transaction_date'] = pd.to_datetime(df['transaction_date'])

        cutoff = pd.Timestamp.today() - pd.DateOffset(months=13) # we set the cuto off months to 13 months

        df = df.loc[df['transaction_date'] >= cutoff]
        df['cohort_period'] = df['transaction_date'].dt.to_period('M')

        cohort_ungrouped = df 
        cohort_size = df.groupby('cohort_period').agg({'sender_id': 'nunique'}).reset_index().rename(columns={'sender_id':'num_users_cohort_size'})
        return cohort_ungrouped, cohort_size
    
    except Exception as e:
        raise ValueError(f"Error generating cohort: {e}")
    

# Next we need to get the exploaded table to get the retention numbers
def generate_retention_tbl(df:pd.DataFrame, cohort_ungrouped: pd.DataFrame) ->  pd.DataFrame: 

    try:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['txn_mon_yr'] = df['transaction_date'].dt.to_period('M')

        new_df = pd.merge(cohort_ungrouped[['sender_id', 'cohort_period']], df[['sender_id', 'txn_mon_yr']], on='sender_id', how='inner')

        new_df['months_since_joining'] = (new_df['txn_mon_yr'] - new_df['cohort_period']).apply(lambda x: x.n )
        new_df = new_df.groupby(['cohort_period', 
                                'months_since_joining',]).agg({'sender_id': 'nunique'}).reset_index().rename(columns= {'sender_id': 'num_users'})
        
        return new_df
    
    except Exception as e:
        raise ValueError(f"Error retention table: {e}")
    

# Finally, we generate the cohort table
def generate_cohort_table(cohort_size: pd.DataFrame, new_df:pd.DataFrame) -> pd.DataFrame:
    try:

        cohort_table = pd.merge(cohort_size, new_df, on='cohort_period', how='left')

        cohort_table['retention_rate'] = cohort_table.apply(lambda x: 
                                                            round(x['num_users'] / x['num_users_cohort_size'] if x ['num_users_cohort_size'] > 0 else 0, 2),  axis=1) * 100
        
        df = pd.pivot_table(cohort_table, index='cohort_period', columns='months_since_joining', values='retention_rate').fillna(0)
        return df
    
    except Exception as e:
         raise ValueError(f"Error cohort table: {e}")




    


