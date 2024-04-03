import requests

def search_umls(icd_code):
    api_key = 'YOUR_UMLS_API_KEY'
    base_url = 'https://uts-ws.nlm.nih.gov/rest'
    endpoint = f'/search/current?string={icd_code}&ticket={api_key}'
    response = requests.get(base_url + endpoint)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_icd_properties(icd_code):
    data = search_umls(icd_code)
    if data:
        # 解析返回的数据，提取ICD代码的属性信息
        # 这里可以根据您的需求从返回的数据中提取症状、体征、实验室检查、药物、治疗等属性信息
        properties = {}
        for result in data['result']['results']:
            concept = result['ui']
            name = result['name']
            properties[concept] = name
        return properties
    else:
        return None

# 示例用法
icd_code = 'I10'  # 替换为您想要查询的ICD-9代码
icd_properties = get_icd_properties(icd_code)
print("ICD属性信息:", icd_properties)