from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_receipts_bronze (**kwargs):
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
            client.command(f"ALTER TABLE rest_staging_area.receipts_bronze DROP PARTITION '{working_date}'")
            client.command(f"ALTER TABLE rest_staging_area.receipt_items_bronze DROP PARTITION '{working_date}'")
            print(f"Партиция за {working_date} очищена.")
        except Exception:
            print(f"Очищать за {working_date} нечего.")


        insert_receipts_data = f"""
            INSERT INTO rest_staging_area.receipts_bronze
            (
	            receipt_id,
	            receipt_time,
	            staff_id,
	            total_price,
	            table_id,
	            client_id,
	            discount_amount,
	            final_price
            )
            SELECT
	            receipt_id,
	            receipt_time,
	            staff_id,
	            total_price,
	            table_id,
	            client_id,
	            discount_amount,
	            final_price
            FROM postgres_dwh.receipts
            WHERE toDate(receipt_time) = '{working_date}'
            UNION ALL
            SELECT
	            receipt_id,
	            receipt_time,
	            staff_id,
	            total_price,
	            table_id,
	            client_id,
	            discount_amount,
	            final_price
            FROM postgres_dwh.receipts
            WHERE toDate(receipt_time) = '{working_date}'
            AND rand() % 100 < 15
        """
        client.command(insert_receipts_data)

        insert_receipt_items_data = f"""
            INSERT INTO rest_staging_area.receipt_items_bronze
            (
                receipt_id,
                receipt_date,
                item_id,
                quantity,
                price_per_item,
                total_price
            )
            SELECT
                receipt_id,
                toDate('{working_date}') as receipt_date,
                item_id,
                quantity,
                price_per_item,
                total_price
            FROM postgres_dwh.receipt_items
            WHERE receipt_id IN (
                SELECT receipt_id
                FROM postgres_dwh.receipts
                WHERE toDate(receipt_time) = '{working_date}'  
            )
            UNION ALL
            SELECT
                receipt_id,
                toDate('{working_date}') as receipt_date,
                item_id,
                quantity,
                price_per_item,
                total_price
            FROM postgres_dwh.receipt_items
            WHERE receipt_id IN (
                SELECT receipt_id
                FROM postgres_dwh.receipts
                WHERE toDate(receipt_time) = '{working_date}'  
            )
            AND rand() % 100 < 15
        """
        client.command(insert_receipt_items_data)

        check_total_receipts = f"SELECT COUNT(*) FROM rest_staging_area.receipts_bronze WHERE toDate(receipt_time) = '{working_date}'"
        downloaded_receipts = client.command(check_total_receipts)

        check_total_items = f"SELECT COUNT(*) FROM rest_staging_area.receipt_items_bronze WHERE receipt_date = '{working_date}'"
        downloaded_items = client.command(check_total_items)

        print(f"Чеки, в количестве {downloaded_receipts} за {working_date} успешно загружены в rest_staging_area.receipts_bronze")
        print(f"Блюда, в количестве {downloaded_items} за {working_date} успешно загружены в rest_staging_area.receipt_items_bronze")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e