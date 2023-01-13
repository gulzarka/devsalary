import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv

HH_URL = 'https://api.hh.ru/vacancies/'
SJ_URL = 'https://api.superjob.ru/2.0/vacancies/'
LANGUAGES = ['Python','Java Script', 'Ruby', 'Go', 'C', 'C++', 'CSS', 'PHP', 'C#', 'Java']

def get_info_all_pages_for_HH(language):
    page = 0
    pages_number = 1
    pages_response = []
    while page < pages_number:
        params = {'page': page, 'text': f'Программист {language}', 
        'area': '1','only_with_salary': True,  'period': '1'}         
        page_response = requests.get(HH_URL, params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        pages_number = page_payload['pages']
        pages_response.append(page_payload)
        page += 1
    return pages_response
       

def get_salary_info_for_HH(response):
    salaries_from = []
    salaries_to = []
    for vacancies in response:
        vacancy = vacancies['items']
        vacancies_found = vacancies['found']
        for vacancy in vacancy:
            salary_currency = vacancy['salary']['currency']
            if salary_currency != 'RUR':
                continue
            salary_from = vacancy['salary']['from']
            salaries_from.append(salary_from)
            salary_to = vacancy['salary']['to']
            salaries_to.append(salary_to)     
    return {'salary_from': salaries_from, 
            'salary_to': salaries_to,
            'found': vacancies_found}


def calculate_average_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        return round(salary_from * 1.2)
    if salary_to and not salary_from:
        return round(salary_to * 0.8)    
    if salary_from  and salary_to:
        return (salary_from + salary_to) // 2  
    return False   
        
 
def get_vacancy_statistics(salary_info, language):        
    vacancies_found = salary_info['found']
    average_salaries = []
    for salary_from in salary_info['salary_from']:
        salary_from = salary_from
    for salary_to in salary_info['salary_to']:
        salary_to = salary_to
        average_salary = calculate_average_salary(salary_from, salary_to)
        average_salaries.append(average_salary)
    total_average_salary = sum(average_salaries) // len(average_salaries)
    output = {language: {'vacancies_found': vacancies_found,  
                        'vacancies_processed': len(average_salaries),
                        'average_salary': total_average_salary}}  
    return output 
   
                 
def get_info_all_pages_for_SJ(language):
    load_dotenv('access_token.env')
    sj_access_token = os.environ['SUPER_JOB_TOKEN']
    page = 0
    pages_number = 1
    pages_response = []
    while page < pages_number:
        params = {'town': 4, 'keyword': language, 'no_agreement': 1, 
                'page': page, 'currency': 'rub', 'catalogues': 48}
        headers = {'X-Api-App-Id': sj_access_token}
        page_response = requests.get(SJ_URL, headers=headers, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()
        vacancy_count = page_payload['total']
        if not vacancy_count < 20:
            pages_number = int(vacancy_count*0.1)
            pages_response.append(page_payload)
            page += 1
    return pages_response


def get_salary_info_for_SJ(response):
    salaries_from = []
    salaries_to =[]
    for vacancies in response:
        vacancy = vacancies['objects']
        vacancies_found = vacancies['total']
        for vacancy in vacancy:  
            salary_from = vacancy['payment_from']
            salaries_from.append(salary_from)
            salary_to = vacancy['payment_to'] 
            salaries_to.append(salary_to)
    return {'salary_from': salaries_from,
            'salary_to': salaries_to,
            'found': vacancies_found} 


def get_stat_table_HH():
    vacancies_table = [('Programming language',
                    'Vacancies found',
                    'Vacancies processed',
                    'Average salary')]                               
    for language in LANGUAGES: 
        vacancy_info = get_salary_info_for_HH(get_info_all_pages_for_HH(language))
        vacancy_statistics = get_vacancy_statistics(vacancy_info, language)        
        for language, salary_stat in vacancy_statistics.items():
            lang = language
            found = salary_stat['vacancies_found']
            salary = salary_stat['average_salary']
            processed = salary_stat['vacancies_processed']
            vacancies_table.append((lang, found, processed, salary))  
    table_instance = AsciiTable(vacancies_table, 'Head Hunter Moscow')
    return table_instance.table         


def get_stat_table_SJ():
    vacancies_table = [(
                    'Programming language',
                    'Vacancies found',
                    'Vacancies processed',
                    'Average salary'
                )]        
    for language in LANGUAGES: 
        vacancy_info = get_salary_info_for_SJ(get_info_all_pages_for_SJ(language))
        vacancy_statistics = get_vacancy_statistics(vacancy_info, language)        
        for language, salary_stat in vacancy_statistics.items():
            lang = language
            found = salary_stat['vacancies_found']
            salary = salary_stat['average_salary']
            processed = salary_stat['vacancies_processed']
            vacancies_table.append((lang, found, processed, salary))  
    table_instance = AsciiTable(vacancies_table, 'Super Job Moscow')
    return table_instance.table     

def main():
    print(get_stat_table_HH())
    print(get_stat_table_SJ())


if __name__ == "__main__":
    main()
