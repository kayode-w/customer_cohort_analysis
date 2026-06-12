from db_conn import db_connection
import pandas as pd 
from datetime import datetime, timedelta

engine = db_connection()


# Fist function for loading the tables in, we could choose to pass in a single table or a list of tables and store in a dict. 
def load_tables(tbl_name: str | list) -> pd.DataFrame:
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
                tables[tbl] = #query asigning the query result to the corresponding table name in the tables dictionary
            return tables       
        except Exception as e:
            raise ValueError(f"Error loading table: {tbl}: {e}")

    else:
        raise TypeError("tbl_name must be a string or a list of strings.")

    
# Next step is to extract the cohort period (month and year) from the created_at column, we can create a function for this as well.
def extract_cohort_period(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    try:
        df[col_name] = pd.to_datetime(df[col_name]) # We first need to convert the column to a datetime object
        df['cohort_period'] = df[col_name].dt.to_period('M')  # Next we need to xtract the cohort period from the created_at date.
        return df

    except Exception as e:
        raise ValueError(f"Error extracting cohort period from column {col_name}: {e}")
    
    
def get_cohort_analysis(users: pd.Data_Frame, txn: pd.DataFrame) -> pd.DataDFrame:
    '''
    This function will perform the cohort analysis by calculating the number of users in each cohort and their retention over time.
    It will take a single pd.DataFrame as input andreturn a DataFrame with the cohort analysis results.
    '''
    try:
        # Now we merge both tables to bring the transacion date into the users table. 
        new_df = pd.merge(users[['user_id', 'cohort_period']], txn[['sender_id', 'transaction_date']], left_on='user_id', right_on='sender_id', how='left')
        new_df = new_df.drop(columns=['sender_id']) #We drop the redundant table.

        new_df['transaction_date'] = pd.to_datetime(new_df['transaction_date']) #We also convert this to datetime.
        new_df['transaction_period'] = new_df['transaction_date'].dt.to_period('M') # We extract the transaction period from the transaction date.

        #we use lambda x.n to unpack the number within the 'period' object the subtraction returns and gives just a number.
        months_since_joining = (new_df['transaction_period'] - new_df['cohort_period']).apply(lambda x: x.n) 



    except Exception as e:
        raise ValueError(f"Error performing cohort analysis: {e}")