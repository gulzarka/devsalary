import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv

LANGS = ['Python', 'Java Script', 'Ruby', 'Go', 'C',
         'C++', 'CSS', 'PHP', 'C#', 'Java']


def get_response_all_pages_hh(language):
    url = 'https://api.hh.ru/vacancies/'
    moscow_code = 1
    searching_period = 1
    page = 0
    pages_number = 1
    pages_response = []
    while page < pages_number:
        params = {
            'page': page, 'text': f'Программист {language}',
            'area': moscow_code, 'only_with_salary': True,
            'period': searching_period
        }
        page_response = requests.get(url, params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        pages_response.append(page_payload)
        page += 1
    return pages_response


def calculate_average_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return round(salary_from * 1.2)
    if salary_to and not salary_from:
        return round(salary_to * 0.8)
    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    return False

    


def calculate_total_average_salary(average_salaries):
    try:
        total_average_salary = sum(average_salaries) // len(average_salaries)
    except ZeroDivisionError:
        return 0
    return total_average_salary


def predict_rubl_salaries_hh(response, language):
    average_salaries = []
    for vacancies in response:
        vacancies_found = vacancies['found']
        vacancies = vacancies['items']
        for vacancy in vacancies:
            salary_currency = vacancy['salary']['currency']
            if not salary_currency == 'RUR':
                return None
            salary_from = vacancy['salary']['from']
            salary_to = vacancy['salary']['to']
            average_salary = calculate_average_salary(salary_from, salary_to)
            if not average_salary:
                continue
            average_salaries.append(average_salary)
        total_average_salary = calculate_total_average_salary(average_salaries)
        salary_statistics = {language: {
                            'vacancies_found': vacancies_found,
                            'vacancies_processed': len(average_salaries),
                            'average_salary': total_average_salary
                            }
                            }
    return salary_statistics


def get_stat_table_hh():
    stat_table = [(
                    'Programming language',
                    'Vacancies found',
                    'Vacancies processed',
                    'Average salary'
                )]
    for language in LANGS:
        salaries = predict_rubl_salaries_hh(
            get_response_all_pages_hh(language), language
            )
        for language, salary_stat in salaries.items():
            lang = language
            found = salary_stat['vacancies_found']
            salary = salary_stat['average_salary']
            processed = salary_stat['vacancies_processed']
            stat_table.append((lang, found, processed, salary))
            table_instance = AsciiTable(stat_table, 'Head Hunter Moscow')
    return table_instance.table


def get_response_all_pages_sj(language, access_token):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    moscow_code = 4
    page = 0
    pages_number = 1
    pages_response = []
    vacancy_per_page = 10
    programmer_id = 48
    params = {'town': moscow_code, 'keyword': language,
              'count': vacancy_per_page,
              'page': page, 'currency': 'rub',
              'catalogues': programmer_id}
    headers = {'X-Api-App-Id': access_token}
    while page < pages_number:
        page_response = requests.get(url, headers=headers, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        vacancy_count = page_payload['total']
        if not vacancy_count < vacancy_per_page:
            pages_number = int(vacancy_count/vacancy_per_page)
            pages_response.append(page_payload)
            page += 1
    return pages_response


def predict_rubl_salaries_sj(response, language):
    average_salaries = []
    for vacancies in response:
        vacancies = vacancies['objects']
        vacancies_found = vacancies['total']
        for vacancy in vacancies:
            salary_from = vacancy['payment_from']
            salary_to = vacancy['payment_to']
            average_salary = calculate_average_salary(salary_from, salary_to)
            if not average_salary:
                continue
            average_salaries.append(average_salary)
    total_average_salary = calculate_total_average_salary(average_salaries)
    salary_statistics = {language:
                         {'vacancies_found': vacancies_found,
                          'vacancies_processed': len(average_salaries),
                          'average_salary': total_average_salary}}
    return salary_statistics


def get_stat_table_sj(access_token):
    stat_table = [(
                    'Programming language',
                    'Vacancies found',
                    'Vacancies processed',
                    'Average salary'
                )]
    for language in LANGS:
        salaries = predict_rubl_salaries_sj(
            get_response_all_pages_sj(language, access_token), language
            )
        for language, salary_stat in salaries.items():
            lang = language
            found = salary_stat['vacancies_found']
            salary = salary_stat['average_salary']
            processed = salary_stat['vacancies_processed']
            stat_table.append((lang, found, processed, salary))
            table_instance = AsciiTable(stat_table, 'Head Hunter Moscow')
    return table_instance.table


def main():
    load_dotenv('access_token.env')
    sj_access_token = os.environ['SUPER_JOB_TOKEN']
    print(get_stat_table_sj(sj_access_token))
    print(get_stat_table_hh())


if __name__ == "__main__":
    main()
