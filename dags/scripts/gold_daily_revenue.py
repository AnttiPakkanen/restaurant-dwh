from airflow.hooks.base import BaseHook
import clickhouse_connect

def daily_revenue (**kwargs):
    working_date = kwargs['ds']
    print(f"Начинаем загрузку daily_revenue за дату: {working_date}")

    connect_ch = BaseHook.get_connection('clickhouse_cloud')
    client = clickhouse_connect.get_client(
        host=connect_ch.host,
        port=connect_ch.port,
        username=connect_ch.login,
        password=connect_ch.password,
        secure=False
    )

    try:
        try:
            client.command(f"ALTER TABLE rest_data_marts.daily_revenue DROP PARTITION '{working_date}'")
            print(f"Партиция за {working_date} удалена.")
        except Exception:
            print(f"Очищать за {working_date} нечего.")

        insert_data = f"""
            INSERT INTO rest_data_marts.daily_revenue
            (
                report_date,
	            total_receipts,
	            total_revenue,
	            total_discount,
	            avg_receipt_value
            )
            SELECT
                toDate('{working_date}') AS report_date,
                COUNT(receipt_id) AS total_receipts,
                SUM(final_price) AS total_revenue,
                SUM(discount_amount) AS total_discount,
                AVG(final_price) AS avg_receipt_value
            FROM rest_dim_model.receipts_silver FINAL
            WHERE receipt_time >= '{working_date} 00:00:00'
                AND receipt_time <= '{working_date} 23:59:59'
            GROUP BY report_date
        """
        client.command(insert_data)

        silver_check = f"""
            SELECT SUM(final_price) as silver_revenue
            FROM rest_dim_model.receipts_silver FINAL
            WHERE receipt_time >= '{working_date} 00:00:00'
                AND receipt_time <= '{working_date} 23:59:59'
        """
        silver_result = client.query(silver_check).named_results()
        silver_list = list(silver_result)
        silver_revenue = silver_list[0]['silver_revenue'] if silver_list and silver_list[0]['silver_revenue'] else 0.0

        gold_check = f"""
            SELECT total_receipts, total_revenue 
            FROM rest_data_marts.daily_revenue 
            WHERE report_date = '{working_date}'
        """
        gold_result = client.query(gold_check).named_results()
        gold_list = list(gold_result)

        if gold_list:
            row = gold_list[0]
            receipts_count = row['total_receipts']
            gold_revenue = row['total_revenue']
            print(f"Чеков: {receipts_count}. Выручка: {gold_revenue}")
            assert round(silver_revenue, 2) == round(gold_revenue, 2), f"Ошибка! Потеряна выручка. Должно быть: {silver_revenue}. Загружено: {gold_revenue} "
        else:
            print(f"Внимание: За {working_date} нет данных для расчета.")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e