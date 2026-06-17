from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_receipts_silver (**kwargs):
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
            client.command(f"ALTER TABLE rest_dim_model.receipts_silver DROP PARTITION '{working_date}'")
            client.command(f"ALTER TABLE rest_dim_model.receipt_items_silver DROP PARTITION '{working_date}'")
            print(f"Партиция за {working_date} очищена.")
        except Exception:
            print(f"Очищать за {working_date} нечего.")

        insert_receipts_data = f"""
            INSERT INTO rest_dim_model.receipts_silver
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
	            COALESCE(staff_id, toUUID('00000000-0000-0000-0000-000000000000')) as staff_id,
	            COALESCE(total_price, CAST(0 AS Decimal(10, 2))) as total_price,
	            COALESCE(table_id, -1) as table_id,
	            COALESCE(client_id, toUUID('00000000-0000-0000-0000-000000000000')) as client_id,
	            COALESCE(discount_amount, CAST(0 AS Decimal(10, 2))) as discount_amount,
	            COALESCE(final_price, CAST(0 AS Decimal(10, 2))) as final_price
            FROM rest_staging_area.receipts_bronze
            WHERE toDate(receipt_time) = '{working_date}'
        """
        client.command(insert_receipts_data)

        insert_receipt_items_data = f"""
            INSERT INTO rest_dim_model.receipt_items_silver
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
                receipt_date,
                item_id,
                COALESCE(quantity, 1) as quantity,
                COALESCE(price_per_item, CAST(0 AS Decimal(10, 2))) as price_per_item,
                COALESCE(total_price, CAST(0 AS Decimal(10, 2))) as total_price
            FROM rest_staging_area.receipt_items_bronze
            WHERE receipt_date = '{working_date}'
        """
        client.command(insert_receipt_items_data)

        check_total_receipts = f"SELECT COUNT(*) FROM rest_dim_model.receipts_silver FINAL WHERE toDate(receipt_time) = '{working_date}'"
        downloaded_receipts = client.command(check_total_receipts)

        check_total_items = f"SELECT COUNT(*) FROM rest_dim_model.receipt_items_silver FINAL WHERE receipt_date = '{working_date}'"
        downloaded_items = client.command(check_total_items)

        print(f"Чеки, в количестве {downloaded_receipts} за {working_date} успешно загружены в rest_dim_model.receipts_silver")
        print(f"Блюда, в количестве {downloaded_items} за {working_date} успешно загружены в rest_dim_model.receipt_items_silver")

    
    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e