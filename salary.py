import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv

LANGS = ['Python', 'Java Script', 'Ruby', 'Go', 'C',
         'C++', 'CSS', 'PHP', 'C#', 'Java']


def get_response_all_pages_HH(language):
    url = 'https://api.hh.ru/vacancies/'
    moscow_code = 1
    publishing_days = 1
    page = 0
    pages_number = 1
    pages_response = []
    while page < pages_number:
        params = {
            'page': page, 'text': f'Программист {language}',
            'area': moscow_code, 'only_with_salary': True,
            'period': publishing_days
        }
        page_response = requests.get(url, params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        pages_response.append(page_payload)
        page += 1
    return pages_response


def get_salaries_HH(response):
    salaries_from = []
    salaries_to = []
    for vacancies in response:
        vacancies_found = vacancies['found']
        vacancies = vacancies['items']
        for vacancy in vacancies:
            salary_currency = vacancy['salary']['currency']
            if salary_currency == 'RUR':
                salary_from = vacancy['salary']['from']
                salaries_from.append(salary_from)
                salary_to = vacancy['salary']['to']
                salaries_to.append(salary_to)
            None
    return {
            'salaries_from': salaries_from,
            'salaries_to': salaries_to,
            'found': vacancies_found
            }


def calculate_average_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return round(salary_from * 1.2)
    if salary_to and not salary_from:
        return round(salary_to * 0.8)
    if salary_from and salary_to:
        return (salary_from + salary_to) // 2
    return False


def get_vacancy_statistics(salaries, language):
    average_salaries = []
    vacancies_found = salaries['found']
    salaries_from = salaries['salaries_from']
    for salary_from in salaries_from:
        salary_from = salary_from
    for salary_to in salaries['salaries_to']:
        salary_to = salary_to
        average_salary = calculate_average_salary(salary_from, salary_to)
        average_salaries.append(average_salary)
    try:
        total_average_salary = sum(average_salaries) // len(average_salaries)
    except ZeroDivisionError:
        return 'Zero division error'
    vacancy_statistics = {language:
                          {'vacancies_found': vacancies_found,
                           'vacancies_processed': len(average_salaries),
                           'average_salary': total_average_salary}}
    return vacancy_statistics


def get_response_all_pages_SJ(language, access_token):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    moscow_code = 4
    page = 0
    pages_number = 1
    pages_response = []
    only_with_salary = 1
    programmer_id = 48
    params = {'town': moscow_code, 'keyword': language,
              'no_agreement': only_with_salary,
              'page': page, 'currency': 'rub',
              'catalogues': programmer_id}
    headers = {'X-Api-App-Id': access_token}
    while page < pages_number:
        page_response = requests.get(url, headers=headers, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        vacancy_count = page_payload['total']
        if not vacancy_count < 20:
            pages_number = int(vacancy_count*0.1)
            pages_response.append(page_payload)
            page += 1
    return pages_response


def get_salaries_SJ(response):
    salaries_from = []
    salaries_to = []
    for vacancies in response:
        vacancies = vacancies['objects']
        vacancies_found = vacancies['total']
        for vacancy in vacancies:
            salary_from = vacancy['payment_from']
            salaries_from.append(salary_from)
            salary_to = vacancy['payment_to']
            salaries_to.append(salary_to)
    return {'salaries_from': salaries_from,
            'salaries_to': salaries_to,
            'found': vacancies_found}


def parse_vacancy_statistics(vacancy_statistics):
    for language, salary_stat in vacancy_statistics.items():
        lang = language
        found = salary_stat['vacancies_found']
        salary = salary_stat['average_salary']
        processed = salary_stat['vacancies_processed']
        return lang, found, salary, processed


def get_stat_table_HH():
    vacancies_table = [('Programming language',
                        'Vacancies found',
                        'Vacancies processed',
                        'Average salary')]
    for language in LANGS:
        vacancies = get_salaries_HH(get_response_all_pages_HH(language))
        vacancy_statistics = get_vacancy_statistics(vacancies, language)
        lang, found, salary, processed = parse_vacancy_statistics(vacancy_statistics)
        vacancies_table.append((lang, found, processed, salary))
    table_instance = AsciiTable(vacancies_table, 'Head Hunter Moscow')
    return table_instance.table


def get_stat_table_SJ(access_token):
    vacancies_table = [(
                    'Programming language',
                    'Vacancies found',
                    'Vacancies processed',
                    'Average salary'
                )]
    for language in LANGS:
        vacancies = get_salaries_SJ(get_response_all_pages_SJ(language, access_token))
        vacancy_statistics = get_vacancy_statistics(vacancies, language)
        lang, found, salary, processed = parse_vacancy_statistics(vacancy_statistics)
        vacancies_table.append((lang, found, processed, salary))
    table_instance = AsciiTable(vacancies_table, 'Super Job Moscow')
    return table_instance.table


def main():
    load_dotenv('access_token.env')
    sj_access_token = os.environ['SUPER_JOB_TOKEN']
    print(get_stat_table_SJ(sj_access_token))
    print(get_stat_table_HH())


if __name__ == "__main__":
    main()
