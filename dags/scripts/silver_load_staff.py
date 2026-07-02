from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_staff_in_silver (**kwargs):
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
        delete_old_staff_data = f"""
            ALTER TABLE rest_dim_model.staff_silver
            UPDATE valid_to = toDate('{working_date}') - 1, is_current = 0
            WHERE is_current = 1 AND staff_id IN (
                SELECT sst.staff_id
                FROM rest_dim_model.staff_silver as sst
                JOIN rest_staging_area.staff_bronze as bst ON sst.staff_id = bst.staff_id
                WHERE sst.is_current = 1 AND (
                    sst.staff_name != COALESCE(bst.staff_name, 'Неизвестно') OR
                    sst.staff_position != COALESCE(bst.staff_position, 'Без позиции')
                )
            )
            SETTINGS mutations_sync = 1
        """
        client.command(delete_old_staff_data)
        print("Старая версия списка сотрудников закрыта.")

        insert_staff_data = f"""
            INSERT INTO rest_dim_model.staff_silver
            (
	            staff_id,
	            staff_name,
	            staff_position,
                valid_from,
                valid_to,
                is_current
            )
            SELECT
	            bst.staff_id AS staff_id,
	            COALESCE(bst.staff_name, 'Неизвестно') AS staff_name,
	            COALESCE(bst.staff_position, 'Без позиции') AS staff_position,
                toDate('{working_date}') AS valid_from,
                toDate('2999-12-31') AS valid_to,
                1 AS is_current
            FROM rest_staging_area.staff_bronze AS bst
            LEFT ANTI JOIN rest_dim_model.staff_silver AS sst
                ON bst.staff_id = sst.staff_id AND sst.is_current = 1
        """
        client.command(insert_staff_data)

        check_staff_data = f"SELECT COUNT(*) FROM rest_dim_model.staff_silver WHERE is_current = 1"
        current_staff_data = client.command(check_staff_data)

        print(f"Справочник успешно обновлен. Актуальное количество строк: {current_staff_data}")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e