import requests

def search_wikipedia(icd_code):
    base_url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': icd_code
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_icd_properties(icd_code):
    data = search_wikipedia(icd_code)
    if data and 'query' in data and 'search' in data['query']:
        # 获取搜索结果中的第一个页面标题
        first_result_title = data['query']['search'][0]['title']
        # 获取页面内容
        content = get_wikipedia_content(first_result_title)
        # 在页面内容中搜索症状、体征、实验室检查、药物、治疗等属性信息
        # 这里可以根据页面内容的格式和结构来提取您感兴趣的信息
        # 由于Wikipedia的页面内容可能会有很大差异，您可能需要编写复杂的解析逻辑来提取属性信息
        return content
    else:
        return None

def get_wikipedia_content(title):
    base_url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'explaintext': True,
        'titles': title
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        page_id = list(data['query']['pages'].keys())[0]
        return data['query']['pages'][page_id]['extract']
    else:
        return None

# 示例用法
icd_code = 'Hypertension'  # 替换为您想要查询的疾病名称或关键词
icd_properties = get_icd_properties(icd_code)
print("ICD属性信息:", icd_properties)
