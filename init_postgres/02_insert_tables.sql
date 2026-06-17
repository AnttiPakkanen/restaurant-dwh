-- Наполнение таблицы tables
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (1, 'VIP', 6) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (2, 'VIP', 6) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (3, 'Основной зал', 4) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (4, 'Основной зал', 4) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (5, 'Основной зал', 4) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (6, 'Основной зал', 4) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (7, 'Основной зал', 4) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (8, 'Терраса', 2) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (9, 'Терраса', 2) ON CONFLICT (table_id) DO NOTHING;
INSERT INTO list_of_tables (table_id, zone_name, capacity) VALUES (10, 'Терраса', 2) ON CONFLICT (table_id) DO NOTHING;
