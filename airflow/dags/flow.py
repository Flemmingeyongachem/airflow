from airflow import DAG
from airflow.utils.edgemodifier import Label
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.ssh.hooks.ssh import SSHHook


default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

hook = SSHHook(
    remote_host='192.168.1.171',
    username='HP',
    password='admin',
    port=22,
)

with DAG(
    'test_dag',
    description='This is my first DAG to learn BASH operation, SSH connection, and transfer data among jobs',
    default_args=default_args,
    start_date=datetime(2021, 6, 10),
    schedule_interval="0 * * * *",
    tags=['Testing', 'Tutorial'],
    catchup=False,
) as dag:
    
    # Task to read local IP
    Read_my_IP = BashOperator(
        task_id='Read_my_IP',
        bash_command="hostname -i | awk '{print $1}'",
    )

    # Task to read remote IP, using XCom for passing IP address
    Read_remote_IP = SSHOperator(
        task_id='Read_remote_IP',
        ssh_hook=hook,
        command="echo {{ ti.xcom_pull(task_ids='Read_my_IP') }}",
    )

    # Declare relationship between tasks
    Read_my_IP >> Label("Pi's IP address") >> Read_remote_IP
