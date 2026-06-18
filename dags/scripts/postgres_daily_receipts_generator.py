from airflow.providers.postgres.hooks.postgres import PostgresHook
import uuid
import random
import pytz
from collections import Counter
from datetime import datetime
from psycopg2.extras import execute_values

def daily_receipts_generator(**kwargs):
    target_date_str = kwargs['ds']
    current_date = datetime.strptime(target_date_str, '%Y-%m-%d')
    almaty_tz = pytz.timezone('Asia/Almaty')

    print(f"Запускаем создание чеков за {current_date.date()}")

    pg_hook = PostgresHook(postgres_conn_id='postgres_cloud')

    with pg_hook.get_conn() as conn_to_database:
        with conn_to_database.cursor() as cursor:

            delete_old_items_query = """
                DELETE FROM receipt_items
                WHERE receipt_id IN (
                    SELECT receipt_id FROM receipts WHERE receipt_time::DATE = %s
                )
            """
            cursor.execute(delete_old_items_query, (current_date.date(), ))

            delete_old_receipts_query = """
                DELETE FROM receipts WHERE receipt_time::DATE = %s
             """
            cursor.execute(delete_old_receipts_query, (current_date.date(), ))

            print("Старые данные удалены.")

            cursor.execute("SELECT staff_id FROM staff WHERE LOWER(staff_position) IN ('официант', 'бармен');")
            staff_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT item_id, price, popularity_weight FROM menu;")
            menu_items = cursor.fetchall()
            weights = [item[2] for item in menu_items]

            cursor.execute("SELECT table_id FROM list_of_tables;")
            table_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT client_id, loyalty_level FROM clients;")
            clients_data = cursor.fetchall()

            discount_map = {
                'Gold': 0.15,
                'Silver': 0.10,
                'Bronze': 0.05
            }

            daily_receipts_count = random.randint(30, 70)
            receipts_batch = []
            items_batch = []

            insert_receipt_query = """
                INSERT INTO receipts (receipt_id, receipt_time, staff_id, total_price, table_id, client_id, discount_amount, final_price)
                VALUES %s
            """

            insert_item_query = """
                INSERT INTO receipt_items (receipt_id, item_id, quantity, price_per_item, total_price)
                VALUES %s
            """

            for _ in range(daily_receipts_count):

                new_receipt_id = str(uuid.uuid4())

                random_hour = random.randint(8, 22)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                naive_receipt_time = current_date.replace(hour=random_hour, minute=random_minute, second=random_second, microsecond=0)
                receipt_time = almaty_tz.localize(naive_receipt_time)

                staff_id = random.choice(staff_ids)
                receipt_total_price = 0

                num_items_in_receipt = random.randint(1, 9)
                chosen_dishes = random.choices(menu_items, weights=weights, k=num_items_in_receipt)
                counted_dishes = Counter(chosen_dishes)
                temp_items_basket = []

                for dish, quantity in counted_dishes.items():
                    dish_id, dish_price, _ = dish
                    
                    total_item_price = dish_price * quantity
                    receipt_total_price += total_item_price

                    temp_items_basket.append((dish_id, quantity, dish_price, total_item_price))

                table_id = random.choice(table_ids)
                discount_amount = 0

                if random.random() < 0.40 and clients_data:
                    client = random.choice(clients_data)
                    discount_percent = discount_map[client[1]]
                    discount_amount = round(float(receipt_total_price) * discount_percent, 2)
                    client_id = client[0]
                else:
                    client_id = None
                
                final_price = round(float(receipt_total_price) - discount_amount, 2)

                receipts_batch.append((new_receipt_id, receipt_time, staff_id, receipt_total_price, table_id, client_id, discount_amount, final_price))
                for item in temp_items_basket:
                    items_batch.append((new_receipt_id, item[0], item[1], item[2], item[3]))

            execute_values(cursor, insert_receipt_query, receipts_batch)
            execute_values(cursor, insert_item_query, items_batch)

            conn_to_database.commit()
            print(f"Успешно сгенерировано чеков: {daily_receipts_count}")