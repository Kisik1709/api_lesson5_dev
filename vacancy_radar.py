import os
import time
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_city_id_for_hh(base_url, country_name, city_name):
    method = "areas"
    url = f"{base_url}/{method}"

    response = requests.get(url)
    response.raise_for_status()
    areas = response.json()

    for country in areas:
        if country["name"] == country_name:
            for city in country["areas"]:
                if city["name"] == city_name:
                    return city["id"]


def fetch_vacancies_for_hh(language):
    base_url = "https://api.hh.ru"

    method = "vacancies"
    url = f"{base_url}/{method}"

    country_name = "Россия"
    city_name = "Москва"
    area_id = get_city_id_for_hh(base_url, country_name, city_name)

    period = 30

    page = 0
    per_page = 100

    params = {
        "area": area_id,
        "period": period,
        "text": f"Программист {language}",
        "per_page": per_page,
        "page": page
    }

    all_vacancies = []
    while page < 19:
        params["page"] = page
        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies = response.json()
        all_vacancies.extend(vacancies["items"])
        page += 1
        time.sleep(0.2)

    return all_vacancies, vacancies["found"]


def predict_rub_salary_for_hh(vacancy):
    salary = vacancy["salary"]
    if salary is None:
        return None
    if salary["currency"] != "RUR":
        return None
    if salary["from"] is not None and salary["to"] is not None:
        salary_from = salary["from"]
        salary_to = salary["to"]
        return (salary_from + salary_to) / 2
    if salary["from"]:
        salary_from = salary["from"]
        return int(salary_from) * 1.2
    if salary["to"]:
        salary_to = salary["to"]
        return int(salary_to) * 0.8
    return None


def get_city_id_for_sj(base_url, api_version, city_name):
    method = "towns"
    url = f"{base_url}/{api_version}/{method}"

    response = requests.get(url)
    response.raise_for_status()
    towns = response.json()

    for town in towns["objects"]:
        if town["title"] == city_name:
            return town["id"]


def fetch_vacancies_for_sj(language, sj_key):
    base_url = "https://api.superjob.ru"
    api_version = 2.2
    method = "vacancies"
    url = f"{base_url}/{api_version}/{method}/"
    headers = {
        "X-Api-App-Id": sj_key
    }
    city_name = "Москва"
    town_id = get_city_id_for_sj(base_url, api_version, city_name)
    page = 0
    per_page = 100
    params = {
        "keyword": f"Программист {language}",
        "town": town_id,
        "page": page,
        "count": per_page
    }

    all_vacancies = []
    while page < 5:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies = response.json()
        all_vacancies.extend(vacancies["objects"])
        page += 1
        time.sleep(0.2)

    return all_vacancies, vacancies["total"]


def predict_rub_salary_for_sj(vacancy):
    if vacancy["payment_from"] in [None, 0] and vacancy["payment_to"] in [None, 0]:
        return None
    if vacancy["payment_from"] is not None and vacancy["payment_to"] is not None:
        salary_from = vacancy["payment_from"]
        salary_to = vacancy["payment_to"]
        return (salary_from + salary_to) / 2
    if vacancy["payment_from"]:
        salary_from = vacancy["payment_from"]
        return int(salary_from) * 1.2
    if vacancy["payment_to"]:
        salary_to = vacancy["payment_to"]
        return int(salary_to) * 0.8
    return None


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


def pack_data_in_table(stats, languages, title_table):
    table_rows = [
        ["Язык программирования", "Найдено вакансий",
         "Обработано вакансий", "Средняя зарплата"]
    ]

    for lang in languages:
        lang_info = [lang,
                     stats[lang]["vacancies_found"],
                     stats[lang]["vacancies_processed"],
                     stats[lang]["average_salary"]
                     ]
        table_rows.append(lang_info)

    table_stats = AsciiTable(table_rows, title_table)
    table_stats.justify_columns[4] = "right"
    return table_stats.table


def main():
    load_dotenv()
    sj_key = os.getenv("SECRET_KEY_SJ")

    languages = [
        "Python", "Java", "JavaScript", "Ruby", "PHP", "C++", "C#", "C", "GO",
        "Shell", "Swift", "TypeScript"
    ]

    hh_stats = collect_language_statistics(
        languages,
        fetch_vacancy_func=fetch_vacancies_for_hh,
        predict_salary_func=predict_rub_salary_for_hh
    )

    sj_stats = collect_language_statistics(
        languages,
        fetch_vacancy_func=fetch_vacancies_for_sj,
        predict_salary_func=predict_rub_salary_for_sj,
        sj_key=sj_key
    )

    print(pack_data_in_table(hh_stats, languages, "HeadHunter Moscow"))
    print(pack_data_in_table(sj_stats, languages, "SuperJob Moscow"))


if __name__ == "__main__":
    main()
