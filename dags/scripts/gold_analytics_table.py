from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_analytics_table (**kwargs):
    working_date = kwargs['ds']
    print(f"Начинаем загрузку за дату: {working_date}")

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
            client.command(f"ALTER TABLE rest_data_marts.analytics_table DROP PARTITION '{working_date}'")
            print(f"Партиция за {working_date} удалена.")
        except Exception:
            print(f"Очищать за {working_date} нечего.")

        insert_items_data = f"""
            INSERT INTO rest_data_marts.analytics_table
            (
                report_date,
                receipt_id,
                receipt_time,
                items,
                total_items_count,
                final_price,
                staff_id,
                staff_name
            )
            WITH t1 AS
            (
                SELECT
		            ris.receipt_id,
		            arraySort(groupUniqArray(ms.dish_name)) AS items,
                    COUNT() as total_items_count
	            FROM rest_dim_model.receipt_items_silver ris 
	            LEFT ASOF JOIN rest_dim_model.menu_silver ms 
		            ON ris.item_id = ms.item_id AND ris.receipt_date >= ms.valid_from
	            WHERE ris.receipt_date = '{working_date}'
	            GROUP BY ris.receipt_id
            )
            SELECT 
                toDate(rs.receipt_time) as report_date,
                rs.receipt_id,
                rs.receipt_time,
                t1.items,
                t1.total_items_count,
                rs.final_price,
                rs.staff_id,
	            ss.staff_name
            FROM rest_dim_model.receipts_silver rs
            JOIN t1 ON rs.receipt_id = t1.receipt_id
            LEFT ASOF JOIN rest_dim_model.staff_silver ss
                ON rs.staff_id = ss.staff_id AND toDate(rs.receipt_time) >= ss.valid_from
            WHERE toDate(rs.receipt_time) = '{working_date}';
        """
        client.command(insert_items_data)

        silver_receipts_count = client.command(f"""
            SELECT COUNT(*)
            FROM rest_dim_model.receipts_silver
            WHERE toDate(receipt_time) = '{working_date}'                        
        """)

        gold_receipts_count = client.command(f"""
            SELECT COUNT(*)
            FROM rest_data_marts.analytics_table
            WHERE report_date = '{working_date}'
        """)

        if silver_receipts_count > 0:
            assert gold_receipts_count > 0, "Ошибка!!! В Silver слое есть чеки, но Gold слой пустой."
            assert silver_receipts_count == gold_receipts_count, f"Ошибка!!! Потеря чеков при JOIN. В Silver слое: {silver_receipts_count}, в Gold слое: {gold_receipts_count}"

        print(f"Все данные за {working_date} загружены")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e