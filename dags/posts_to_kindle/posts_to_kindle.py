import random
from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from airflow.hooks.http_hook import HttpHook
default_args = {
    'owner': 'victor-oliveira',
    'depends_on_past': False,
    'email': ['vt.victoroliveira@gmail.com'],
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'start_date': datetime(2020, 7, 28)
}

dag = DAG(
    dag_id='posts-kindle',
    description='An ETL to send posts to my kindle',
    schedule_interval='@once',
    default_args=default_args
)

def print_xcom(**kargs):
    ti = kargs['task_instance']
    ids = ti.xcom_pull(task_ids='retrieve_hackernews_metadata')
    
    sample_ids = random.sample(ids, k=10)
    hook = HttpHook(method='GET', http_conn_id='hackernews')
    for sample_id in sample_ids:
        response = hook.run(endpoint=f'v0/item/{sample_id}.json?print=pretty')
        print(response.json)
    


start = DummyOperator(
    dag=dag, 
    task_id='start'
    )

retrieve_hackernews_metadata = SimpleHttpOperator(
    dag=dag,
    task_id='retrieve_hackernews_metadata',
    http_conn_id='hackernews',
    endpoint='/v0/topstories.json?print=pretty',
    method='GET',
    xcom_push=True
)

print_collected_data = PythonOperator(
    dag=dag,
    task_id='print_collected_data',
    python_callable=print_xcom,
    provide_context=True
)

start >> retrieve_hackernews_metadata
retrieve_hackernews_metadata >> print_collected_data



