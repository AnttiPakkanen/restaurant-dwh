from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scripts.postgres_daily_receipts_generator import daily_receipts_generator
from scripts.bronze_load_receipts import load_receipts_bronze
from scripts.bronze_load_staff import load_staff_in_bronze
from scripts.bronze_load_menu import load_menu_in_bronze
from scripts.silver_load_receipts import load_receipts_silver
from scripts.silver_load_staff import load_staff_in_silver
from scripts.silver_load_menu import load_menu_in_silver
from scripts.gold_daily_revenue import daily_revenue
from scripts.gold_daily_staff_kpi import load_daily_staff_kpi
from scripts.gold_analytics_table import load_analytics_table

default_args = {
    'owner': 'data_engineer',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id = 'receipts_daily_load',
    default_args = default_args,
    description = 'Ежедневная инкрементальная загрузка данных',
    start_date = datetime(2025, 1, 1),
    schedule_interval = '0 3 * * *',
    catchup = True,
    max_active_runs = 3,
    tags = ['restaurant', 'Postgres', 'Clickhouse']
) as dag:
    
    generate_data_task = PythonOperator(
        task_id='generate_raw_data',
        python_callable=daily_receipts_generator,
    )

    bronze_receipts_task = PythonOperator(
        task_id='load_receipts_bronze',
        python_callable=load_receipts_bronze,
    )

    bronze_staff_task = PythonOperator(
        task_id='load_staff_in_bronze',
        python_callable=load_staff_in_bronze,
    )

    bronze_menu_task = PythonOperator(
        task_id='load_menu_in_bronze',
        python_callable=load_menu_in_bronze,
    )

    silver_receipts_task = PythonOperator(
        task_id='load_receipts_silver',
        python_callable=load_receipts_silver,
    )

    silver_staff_task = PythonOperator(
        task_id='load_staff_in_silver',
        python_callable=load_staff_in_silver,
    )

    silver_menu_task = PythonOperator(
        task_id='load_menu_in_silver',
        python_callable=load_menu_in_silver,
    )

    gold_revenue_task = PythonOperator(
        task_id='daily_revenue',
        python_callable=daily_revenue,
    )

    gold_staff_kpi_task = PythonOperator(
        task_id='load_daily_staff_kpi',
        python_callable=load_daily_staff_kpi,
    )

    gold_analytics_table_task = PythonOperator(
        task_id='load_analytics_table',
        python_callable=load_analytics_table,
    )

    generate_data_task >> [bronze_receipts_task, bronze_staff_task, bronze_menu_task]
    bronze_receipts_task >> silver_receipts_task
    bronze_staff_task >> silver_staff_task
    bronze_menu_task >> silver_menu_task
    [silver_receipts_task, silver_menu_task] >> gold_revenue_task
    [silver_receipts_task, silver_staff_task] >> gold_staff_kpi_task
    [silver_receipts_task, silver_staff_task, silver_menu_task] >> gold_analytics_table_task