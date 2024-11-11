from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.utils.dates import days_ago
from datetime import timedelta

def clean_unused_connections():
    # Use the MySqlHook to connect to the MySQL server
    hook = MySqlHook(mysql_conn_id='ditrosctdb')
    conn = hook.get_conn()
    cursor = conn.cursor()

    try:
        # Query to find all processes with the status "Sleep" (idle connections)
        query = (
            "SELECT ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO "
            "FROM information_schema.PROCESSLIST "
            "WHERE COMMAND = 'Sleep' AND TIME > 60"  # Adjust the TIME threshold as needed
        )
        cursor.execute(query)

        # Fetch all sleeping processes
        sleeping_processes = cursor.fetchall()

        print("Found sleeping processes:")
        for process in sleeping_processes:
            print(process)

        # Kill each sleeping process
        for process in sleeping_processes:
            kill_query = f"KILL {process[0]}"
            cursor.execute(kill_query)
            print(f"Killed connection ID {process[0]}")

        print("Unused connections cleaned up successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

# Define the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='clean_unused_connections_dag',
    default_args=default_args,
    description='A DAG to clean unused MySQL connections',
    schedule_interval='*/2 * * * *', 
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Define the PythonOperator to execute the cleaning function
    clean_connections_task = PythonOperator(
        task_id='clean_connections',
        python_callable=clean_unused_connections,
        provide_context=True
    )

    clean_connections_task
    
    
# from airflow.models.connection import Connection
# import pymysql    

# conn = Connection.get_connection_from_secrets(conn_id='mysql_con')
# conn_dev = pymysql.connect(
#     user=conn.login,
#     password=conn.password,
#     host=conn.host,
#     port=conn.port,
#     database=conn.schema
# )
# cur_dev = conn_dev.cursor()
# cur_dev.execute("SELECT name, email FROM test.tbl_users")
