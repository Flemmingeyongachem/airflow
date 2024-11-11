from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from time import sleep

# Define the DAG and default arguments
default_args = {
    'owner': 'airflow',
}

dag = DAG(
    dag_id='execute_and_check_task',
    default_args=default_args,
    schedule_interval=None,
    start_date=days_ago(1),
)

# Task 1: Move to the Desktop and Execute the Shortcut
execute_shortcut = SSHOperator(
    task_id='execute_shortcut',
    ssh_conn_id='ssh_default',  # Your Airflow SSH connection ID
    command="cd ~/Desktop && ./shortcut.sh",  # Adjust this command if needed
    dag=dag
)

# Task 2: Check if `task.exe` is running every 5 minutes
check_task_running = SSHOperator(
    task_id='check_task_running',
    ssh_conn_id='ssh_default',  # Your Airflow SSH connection ID
    command="tasklist | findstr task.exe",  # Command to find task.exe
    dag=dag
)

# This Python function will be used to periodically check the process
def wait_for_task():
    from airflow.exceptions import AirflowFailException
    while True:
        result = check_task_running.execute(context={})
        if 'task.exe' in result:
            print("task.exe is running.")
            break
        print("task.exe not found, checking again in 5 minutes...")
        sleep(300)  # Wait for 5 minutes

# Task 3: Check `task.exe` status periodically
wait_for_task = PythonOperator(
    task_id='wait_for_task',
    python_callable=wait_for_task,
    dag=dag
)

# Define task dependencies
execute_shortcut >> wait_for_task

