from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_daily_staff_kpi (**kwargs):
    working_date = kwargs['ds']
    print(f"Начинаем загрузку за дату: {working_date}")

    connect_ch = BaseHook.get_connection('clickhouse_cloud')
    client = clickhouse_connect.get_client(
        host=connect_ch.host,
        port=connect_ch.port,
        username=connect_ch.login,
        password=connect_ch.password,
        secure=True
    )

    try:
        client.command(f"ALTER TABLE rest_data_marts.daily_staff_kpi DROP PARTITION IF EXISTS '{working_date}'")
        print("Старая версия таблицы удалена.")

        insert_daily_staff_kpi = f"""
            INSERT INTO rest_data_marts.daily_staff_kpi
            (
	            report_date,
	            staff_id,
                name,
	            staff_position,
                receipts_closed,
                day_revenue,
                avg_receipt_size,
                daily_rank
            )
            SELECT
                toDate('{working_date}') as report_date,
                st.staff_id,
	            st.staff_name AS name,
	            st.staff_position AS staff_position,
	            COUNT(rs.receipt_id) AS receipts_closed,
	            SUM(rs.final_price) AS day_revenue,
	            AVG(rs.final_price) AS avg_receipt_size,
	            DENSE_RANK() OVER (ORDER BY SUM(rs.final_price) DESC) AS daily_rank
            FROM rest_dim_model.receipts_silver FINAL AS rs
            LEFT JOIN rest_dim_model.staff_silver AS st 
	            ON rs.staff_id = st.staff_id AND toDate('{working_date}') BETWEEN st.valid_from AND st.valid_to
            WHERE rs.receipt_time >= '{working_date} 00:00:00'
                AND rs.receipt_time <= '{working_date} 23:59:59'
            GROUP BY report_date, st.staff_id, st.staff_name, st.staff_position;
        """
        client.command(insert_daily_staff_kpi)

        silver_sum = f"""
            SELECT SUM(final_price) FINAL
            FROM rest_dim_model.receipts_silver
            WHERE toDate(receipt_time) = '{working_date}'
        """
        silver_revenue = client.command(silver_sum)

        gold_sum = f"""
            SELECT SUM(day_revenue)
            FROM rest_data_marts.daily_staff_kpi
            WHERE report_date = '{working_date}'
        """
        gold_revenue = client.command(gold_sum)

        assert silver_revenue == gold_revenue, f"ОШИБКА!!! Потеряно {silver_revenue - gold_revenue} тенге при расчете KPI."

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e