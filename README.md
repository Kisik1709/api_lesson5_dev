# 📡 VacancyRadar

VacancyRadar — это утилита для анализа вакансий на платформах HeadHunter и SuperJob. Программа собирает статистику по языкам программирования: количество найденных вакансий, и среднюю зарплату.

## 🚀 Возможности
- Получение актуальных вакансий по списку языков программирования
- Поддержка двух популярных платформ: HH и SuperJob
- Расчёт средней зарплаты
- Вывод статистики в виде таблицы в терминал

## 🔧 Установка

1. Склонируйте репозиторий или скопируйте файлы в свою директорию
2. Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корне проекта и добавьте в него свои ключи:

```bash
SECRET_KEY_SJ=Ваш_ключ_от_SuperJob
```
Получить API-ключ можно на сайте [api.superjob](https://api.superjob.ru)

## ▶️ Использование

```bash
python vacancy_radar.py
```

## 📦 Зависимости
- requests — HTTP-запросы
- python-dotenv — чтение .env-файла
- terminaltables — вывод информации в виде таблицы
- os, time — встроенные модули Python

## 🔗 Используемые API

- [api.hh](https://dev.hh.ru)
- [api.superjob](https://api.superjob.ru)

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org).


