import airflow
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator
from datetime import timedelta
from airflow.operators.python_operator import PythonOperator
import base64


def check_job_running(**kwargs):
    ti = kwargs['ti']
    
    # Get the output of the check_process_task from XCom
    process_output = ti.xcom_pull(task_ids='check_process_task')

    # Log the raw base64-encoded output for debugging
    print(f"Raw Process Output from XCom (base64): {process_output}")
    
    # Decode the base64-encoded output to a string
    try:
        decoded_output = base64.b64decode(process_output).decode('utf-8')
        print(f"Decoded Process Output: {decoded_output}")
    except Exception as e:
        print(f"Error decoding base64 output: {e}")
        decoded_output = process_output  # Fall back to raw output if decoding fails
    
    # Check for the specific message indicating no tasks are running
    if "No tasks are running which match the specified criteria." in decoded_output:
        print("job.exe is not running. Branching to 'ssh_run_command'.")
        return 'ssh_run_command'
    else:
        print("job.exe is already running. Branching to 'do_nothing'.")
        return 'do_nothing'



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'check_and_run_job',
    default_args=default_args,
    schedule_interval=None
    # schedule_interval='*/1 * * * *'  # Run every 1 minutes

)

# Step 1: Define a task to check if job.exe is running using SSH
check_process_task = SSHOperator(
    task_id='check_process_task',
    ssh_conn_id='my_machine',
    command='tasklist /FI "IMAGENAME eq job.exe"',  # For Windows
    do_xcom_push=True,  # Ensure this is True to push the output to XCom
    dag=dag
)

# Step 2: Branching task to decide whether to start the job or do nothing
branching_task = BranchPythonOperator(
    task_id='check_job_status',
    provide_context=True,
    python_callable=check_job_running,
    dag=dag,
)

ssh_task = SSHOperator(
    task_id='ssh_run_command',
    ssh_conn_id='my_machine',
    # command='cd "C:\\Users\\HP\\Desktop\\Filemover\\output\\job" && job.exe',
    command='cd "C:\\Users\\HP\\Desktop\\Filemover\\output\\job" && job.exe',
    # execution_timeout=timedelta(seconds=30),
    dag=dag
)

# schtasks /Create /SC ONCE /TN "MyJob" /TR "C:\\Users\\HP\\Desktop\\Filemover\\output\\job\\job.exe" /ST 12:00 /F

# cd "C:\\Users\\HP\\Desktop\\Filemover\\output\\job" && powershell -Command "Start-Process 'job.exe'"

# Step 4: Define a dummy task for doing nothing if the job is already running
do_nothing = DummyOperator(
    task_id='do_nothing',
    dag=dag
)


# Task 5: Manually triggered task to stop job.exe
# stop_job_task = SSHOperator(
#     task_id='stop_job_task',
#     ssh_conn_id='my_machine',
#     command='taskkill /F /IM job.exe',  # Stop the job.exe process
#     trigger_rule='all_success',  # This ensures that the task can be triggered independently
#     dag=dag
# )

# Step 5: Set task dependencies
check_process_task >> branching_task >> [ssh_task, do_nothing]


# import airflow
# from airflow import DAG
# from airflow.providers.ssh.operators.ssh import SSHOperator
# from airflow.operators.python_operator import BranchPythonOperator
# from airflow.utils.dates import days_ago
# from airflow.operators.dummy import DummyOperator

# def check_job_running(**kwargs):
#     # Use SSHOperator to run the tasklist command and check if job.exe is running
#     ssh_conn_id = 'my_machine'
    
#     check_process = SSHOperator(
#         task_id='check_process_task',
#         ssh_conn_id=ssh_conn_id,
#         command='tasklist /FI "IMAGENAME eq job.exe"',  # For Windows, checks if job.exe is running
#         do_xcom_push=True,
#         dag=kwargs['dag']
#     )
    
#     ti = kwargs['ti']
#     process_output = ti.xcom_pull(task_ids='check_process_task')
    
#     # If job.exe is found in the task list, return the task ID of the 'do_nothing' branch
#     if 'job.exe' in process_output:
#         return 'do_nothing'
#     else:
#         return 'ssh_run_command'

# # Define your DAG
# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'start_date': days_ago(1),
# }

# dag = DAG(
#     'check_and_run_job',
#     default_args=default_args,
#     schedule_interval=None,
# )

# # Step 2: Branching task to check if job.exe is running or not
# branching_task = BranchPythonOperator(
#     task_id='check_job_status',
#     provide_context=True,
#     python_callable=check_job_running,
#     dag=dag,
# )

# # Step 3: Define the task to run the job if it's not already running
# ssh_task = SSHOperator(
#     task_id='ssh_run_command',
#     ssh_conn_id='my_machine',
#     command='cd "C:\\Users\\HP\\Desktop\\Filemover\\output\\job" && job.exe',
#     dag=dag
# )

# # Step 4: Define a dummy task for doing nothing if the job is already running
# do_nothing = DummyOperator(
#     task_id='do_nothing',
#     dag=dag
# )

# # Step 5: Set task dependencies
# branching_task >> [ssh_task, do_nothing]
