from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_menu_in_bronze (**kwargs):
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
        client.command("TRUNCATE TABLE rest_staging_area.menu_bronze")
        print("Старая версия меню удалена.")

        insert_menu_data = f"""
            INSERT INTO rest_staging_area.menu_bronze
            (
	            item_id,
	            category,
	            dish_name,
	            price,
	            popularity_weight
            )
            SELECT
	            item_id,
	            category,
	            dish_name,
	            price,
	            popularity_weight
            FROM postgres_dwh.menu
        """
        client.command(insert_menu_data)

        check_total_menu = f"SELECT COUNT(*) FROM rest_staging_area.menu_bronze"
        downloaded_items = client.command(check_total_menu)

        print(f"Справочник успешно обновлен. Актуальное количество позиций в меню: {downloaded_items} шт.")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e