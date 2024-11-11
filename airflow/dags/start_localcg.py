from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
# from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator    import DummyOperator
# from airflow.models.connection import Connection


dag = DAG(

    'remote_dag',

    default_args={'start_date': days_ago(1)},

    schedule_interval='0 23 * * *',

    catchup=False

)

start_task  = DummyOperator(  task_id= "start", dag=dag )
stop_task   = DummyOperator(  task_id= "stop", dag=dag ) 

ssh_task = SSHOperator( 
    task_id='ssh_run_command',
    ssh_conn_id='my_machine',
    command='cd "C:\\Users\\HP\\Desktop\\Filemover\\output\\job" && job.exe',
    # execution_timeout=timedelta(minutes=5),
    dag=dag
)

start_task>>ssh_task>>stop_task


# # You can use a PythonOperator to call the above function
# from airflow.operators.python_operator import PythonOperator

# run_script_task = PythonOperator(
#     task_id='run_remote_script',
#     python_callable=run_remote_script,
#     dag=dag
# )
