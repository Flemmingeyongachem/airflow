from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from datetime import datetime, timedelta
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.utils.dates import days_ago


dag = DAG(

    'frank_remote_dag',

    default_args={'start_date': days_ago(1)},

    schedule_interval='0 23 * * *',

    catchup=False

)

ssh_task = SSHOperator(
    task_id='ssh_run_command_frank',
    ssh_conn_id='frank_credentials',
    command='cd "C:\\Users\\franc\\Downloads\\Apps\\job\\job" && job.exe',
    execution_timeout=timedelta(minutes=5),
    dag=dag
)

ssh_task

# from airflow.providers.ssh.hooks.ssh import SSHHook

# def run_remote_script():
#     hook = SSHHook(ssh_conn_id='ssh_default')
#     with hook.get_conn() as client:
#         command = "cd ~/Desktop && python your_script.py"
#         stdin, stdout, stderr = client.exec_command(command)
#         print(stdout.read().decode())
#         print(stderr.read().decode())

# # You can use a PythonOperator to call the above function
# from airflow.operators.python_operator import PythonOperator

# run_script_task = PythonOperator(
#     task_id='run_remote_script',
#     python_callable=run_remote_script,
#     dag=dag
# )
# from airflow.providers.ssh.hooks.ssh import SSHHook

# def run_ssh_command():
#     hook = SSHHook(ssh_conn_id='ssh_default')  # Use the Conn Id here
#     with hook.get_conn() as client:
#         stdin, stdout, stderr = client.exec_command('ls -l')
#         print(stdout.read().decode())
#         print(stderr.read().decode())
# ssh_task = SSHOperator(
# task_id='execute_remote_job',
# command='echo Hello from remote server',
# ssh_conn_id='ssh_default',
# username='HP',
# password= "admin",
# port=22,
# timeout=10,
# do_xcom_push=True,
# dag=dag,
# )

# ssh_task



# from airflow import DAG
# from airflow.providers.ssh.operators.ssh import SSHOperator
# from airflow.utils.dates import days_ago
# from datetime import timedelta

# default_args = {
#     'owner': 'your_name',
#     'start_date': days_ago(1),
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'run_windows_script',
#     default_args=default_args,
#     description='A DAG to run a Python script on a remote Windows machine',
#     schedule_interval='@daily',
#     catchup=False,
# )

# run_script_task = SSHOperator(
#     task_id='run_python_script',
#     ssh_conn_id='my_machine',
#     command='python "C:\\Users\\HP\\Desktop\\pyjob\\file_watcher.py"',  # Windows path format
#     timeout=60,
#     dag=dag,
# )

# run_script_task
