-- Наполнение таблицы staff
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('b03d34a1-72dc-4959-964a-e4897e7838ae', 'Феликс Федотович Савин', 'официант') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('e3f36786-e219-4250-a558-c18ae209943a', 'Рыбакова Элеонора Геннадиевна', 'официант') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('6aecb089-9bc9-4cd7-b34a-2490c09e646d', 'Тимофеев Модест Богданович', 'официант') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('adf182b1-236e-4b71-a92f-bdbd80dfb89b', 'Синклитикия Станиславовна Копылова', 'официант') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('e6989002-77eb-495b-9fa8-b8a1c4eed485', 'Владилен Анатольевич Горбачев', 'официант') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('d380b699-f6a8-444c-874a-753e84514ec6', 'Николаева Прасковья Макаровна', 'официант') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('d2e252ee-370e-4f8b-9150-c9fa163f231e', 'Вероника Тимофеевна Баранова', 'бармен') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('8718223b-94f8-4d15-bba3-25553a83e4df', 'Виктор Юлианович Мишин', 'бармен') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('843b069d-0d75-47d7-be03-1bc2cf6e930b', 'тов. Зуев Пантелеймон Анатольевич', 'менеджер зала') ON CONFLICT (staff_id) DO NOTHING;
INSERT INTO staff (staff_id, staff_name, staff_position) VALUES ('bd1de109-b0cd-4335-86b8-a77010513185', 'Кондратий Вилорович Исаков', 'менеджер зала') ON CONFLICT (staff_id) DO NOTHING;
