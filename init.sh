#!/bin/bash
mkdir -p ./dags ./logs ./plugins
cp .env.example .env
USER_ID=$(id -u)

if [ "$USER_ID" -eq 0 ]; then
    echo "Запуск от пользователя root (UID 0)."
    echo "Airflow не может работать от root. Принудительно используем UID 50000 и меняем владельца папок."
    chown -R 50000:0 ./dags ./logs ./plugins
    echo -e "\nAIRFLOW_UID=50000" >> .env
else
    echo "Настройки для локального пользователя (UID $USER_ID)."
    echo -e "\nAIRFLOW_UID=$USER_ID" >> .env
fi

echo "Папки созданы, права настроены в .env!"