from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_staff_in_bronze (**kwargs):
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
        client.command("TRUNCATE TABLE rest_staging_area.staff_bronze")
        print("Старая версия списка сотрудников удалена.")

        insert_staff_data = f"""
            INSERT INTO rest_staging_area.staff_bronze
            (
	            staff_id,
	            staff_name,
	            staff_position
            )
            SELECT
	            staff_id,
	            staff_name,
	            staff_position
            FROM postgres_dwh.staff
        """
        client.command(insert_staff_data)

        check_staff_data = f"SELECT COUNT(*) FROM rest_staging_area.staff_bronze"
        downloaded_staff_data = client.command(check_staff_data)

        print(f"Справочник успешно обновлен. Загружено строк: {downloaded_staff_data}")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e