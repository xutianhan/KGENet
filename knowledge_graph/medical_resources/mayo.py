import requests
from bs4 import BeautifulSoup

def get_disease_info_from_icd9_code(icd9_code):
    try:
        # 使用Clinical Table Search Service API查询ICD-9 code的疾病基本信息
        base_url = "https://clinicaltables.nlm.nih.gov/api/icd9cm_dx/v3/search"
        params = {"terms": icd9_code}
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
        data = response.json()
        if data[0] > 0:
            disease_info = data[3][0]
            print(f"ICD-9 Code: {disease_info[0]}, Disease: {disease_info[1]}")
        else:
            print(f"No disease found for ICD-9 code: {icd9_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while querying Clinical Table Search Service API: {e}")
        return

    try:
        # search in Mayo Clinic
        search_url = "https://www.mayoclinic.org/search/search-results"
        params = {"q": disease_info[1]}
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('a', class_='title')
        if search_results:
            print(f"Mayo Clinic search results for {disease_info[1]}:")
            for result in search_results:
                print(f"Title: {result.text.strip()}, URL: https://www.mayoclinic.org{result['href']}")
        else:
            print(f"No search results found on Mayo Clinic for {disease_info[1]}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while searching Mayo Clinic: {e}")

# example
# get_disease_info_from_icd9_code("250.00")
