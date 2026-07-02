from airflow.hooks.base import BaseHook
import clickhouse_connect

def load_menu_in_silver (**kwargs):
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
        delete_old_menu = f"""
            ALTER TABLE rest_dim_model.menu_silver
            UPDATE valid_to = toDate('{working_date}') - 1, is_current = 0
            WHERE is_current = 1 AND item_id IN (
                SELECT sm.item_id
                FROM rest_dim_model.menu_silver as sm
                JOIN rest_staging_area.menu_bronze as bm ON sm.item_id = bm.item_id
                WHERE sm.is_current = 1 AND (
                    sm.dish_name != COALESCE(bm.dish_name, 'Неизвестно') OR
                    sm.category != COALESCE(bm.category, 'Без категории') OR
                    sm.price != COALESCE(bm.price, CAST(0 AS Decimal(10, 2))) OR
                    sm.popularity_weight != COALESCE(bm.popularity_weight, 0)
                )
            )
            SETTINGS mutations_sync = 1
        """
        client.command(delete_old_menu)
        print("Старая версия меню закрыта.")

        insert_menu_data = f"""
            INSERT INTO rest_dim_model.menu_silver
            (
	            item_id,
	            category,
	            dish_name,
	            price,
	            popularity_weight,
                valid_from,
                valid_to,
                is_current
            )
            SELECT
	            bm.item_id AS item_id,
	            COALESCE(bm.category, 'Без категории') AS category,
	            COALESCE(bm.dish_name, 'Неизвестно') AS dish_name,
	            COALESCE(bm.price, CAST(0 AS Decimal(10, 2))) AS price,
	            COALESCE(bm.popularity_weight, 0) AS popularity_weight,
                toDate('{working_date}') AS valid_from,
                toDate('2999-12-31') AS valid_to,
                1 AS is_current
            FROM rest_staging_area.menu_bronze AS bm
            LEFT ANTI JOIN rest_dim_model.menu_silver AS sm
                ON bm.item_id = sm.item_id AND sm.is_current = 1
        """
        client.command(insert_menu_data)

        check_total_menu = f"SELECT COUNT(*) FROM rest_dim_model.menu_silver WHERE is_current = 1"
        current_menu = client.command(check_total_menu)

        print(f"Справочник успешно обновлен. Актуальное количество позиций в меню: {current_menu} шт.")

    except Exception as e:
        print("Ой! Ошибка!")
        print(e)
        raise e