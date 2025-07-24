import os
import time
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

BASE_URL_HH = "https://api.hh.ru"
BASE_URL_SJ = "https://api.superjob.ru"


def calculate_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return int(salary_from) * 1.2
    if salary_to:
        return int(salary_to) * 0.8


def get_city_id_for_hh(country_name, city_name):
    method = "areas"
    url = f"{BASE_URL_HH}/{method}"

    response = requests.get(url)
    response.raise_for_status()
    areas = response.json()

    for country in areas:
        if country["name"] == country_name:
            for city in country["areas"]:
                if city["name"] == city_name:
                    return city["id"]


def fetch_vacancies_for_hh(language, area_id):
    method = "vacancies"
    url = f"{BASE_URL_HH}/{method}"

    period = 30

    page = 0
    per_page = 100
    max_page = None

    params = {
        "area": area_id,
        "period": period,
        "text": f"Программист {language}",
        "per_page": per_page,
        "page": page
    }

    all_vacancies = []

    while True:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies = response.json()

        if max_page is None:
            max_page = min(vacancies["pages"], 20)

        all_vacancies.extend(vacancies["items"])
        page += 1

        if page >= max_page:
            break

        time.sleep(0.2)

    return all_vacancies, vacancies["found"]


def predict_rub_salary_for_hh(vacancy):
    salary = vacancy["salary"]
    if not salary or salary["currency"] != "RUR":
        return None
    return calculate_salary(salary["from"], salary["to"])


def get_city_id_for_sj(api_version, city_name):
    method = "towns"
    url = f"{BASE_URL_SJ}/{api_version}/{method}"

    response = requests.get(url)
    response.raise_for_status()
    towns = response.json()

    for town in towns["objects"]:
        if town["title"] == city_name:
            return town["id"]


def fetch_vacancies_for_sj(language, sj_key, api_version, town_id):
    method = "vacancies"
    url = f"{BASE_URL_SJ}/{api_version}/{method}/"
    headers = {
        "X-Api-App-Id": sj_key
    }

    page = 0
    per_page = 100
    params = {
        "keyword": f"Программист {language}",
        "town": town_id,
        "page": page,
        "count": per_page
    }

    all_vacancies = []

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies = response.json()

        all_vacancies.extend(vacancies["objects"])

        if not vacancies["more"]:
            break
        page += 1
        time.sleep(0.2)

    return all_vacancies, vacancies["total"]


def predict_rub_salary_for_sj(vacancy):
    if not vacancy["payment_from"] and not vacancy["payment_to"]:
        return None
    return calculate_salary(vacancy["payment_from"], vacancy["payment_to"])


def collect_language_statistics(languages, fetch_vacancy_func, predict_salary_func, **kwargs):
    language_stats = {}

    for lang in languages:
        vacancies, count = fetch_vacancy_func(lang, **kwargs)

        time.sleep(0.2)

        salaries = []
        for vacancy in vacancies:
            salary = predict_salary_func(vacancy)
            if salary:
                salaries.append(salary)
        if salaries:
            average = sum(salaries) / len(salaries)

        language_stats[lang] = {
            "vacancies_found": count,
            "vacancies_processed": len(salaries),
            "average_salary": int(average)
        }

    return language_stats


def pack_data_in_table(stats, title_table):
    table_rows = [
        ["Язык программирования", "Найдено вакансий",
         "Обработано вакансий", "Средняя зарплата"]
    ]

    for lang, lang_stats in stats.items():
        lang_info = [
            lang,
            lang_stats["vacancies_found"],
            lang_stats["vacancies_processed"],
            lang_stats["average_salary"]
        ]
        table_rows.append(lang_info)

    table_stats = AsciiTable(table_rows, title_table)
    table_stats.justify_columns[4] = "right"
    return table_stats.table


def main():
    load_dotenv()

    country_name = "Россия"
    city_name = "Москва"

    area_id_hh = get_city_id_for_hh(country_name, city_name)

    sj_key = os.getenv("SECRET_KEY_SJ")
    api_version = 2.2
    town_id_sj = get_city_id_for_sj(api_version, city_name)

    languages = [
        "Python", "Java", "JavaScript", "Ruby", "PHP", "C++", "C#", "C", "GO",
        "Shell", "Swift", "TypeScript"
    ]

    hh_stats = collect_language_statistics(
        languages,
        fetch_vacancy_func=fetch_vacancies_for_hh,
        predict_salary_func=predict_rub_salary_for_hh,
        area_id=area_id_hh
    )

    sj_stats = collect_language_statistics(
        languages,
        fetch_vacancy_func=fetch_vacancies_for_sj,
        predict_salary_func=predict_rub_salary_for_sj,
        sj_key=sj_key,
        api_version=api_version,
        town_id=town_id_sj
    )

    print(pack_data_in_table(hh_stats, f"HeadHunter {city_name}"))
    print(pack_data_in_table(sj_stats, f"SuperJob {city_name}"))


if __name__ == "__main__":
    main()
