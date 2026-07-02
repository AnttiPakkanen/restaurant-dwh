#!/bin/bash
mkdir -p ./dags ./logs ./plugins
cp .env.example .env
echo -e "\nAIRFLOW_UID=$(id -u)" >> .env
echo "Папки созданы, права (UID $(id -u)) настроены в .env!"