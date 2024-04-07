from WikipediaAPI import Wikipedia
import re

def get_disease_info(disease_name):
    wiki_wiki = Wikipedia('en')
    page_py = wiki_wiki.page(disease_name)

    if not page_py.exists():
        print(f"The page for {disease_name} does not exist.")
        return

    content = page_py.text

    symptoms = re.findall(r'\bsymptoms\b: (.+)', content)

    signs = re.findall(r'\bsigns and symptoms\b: (.+)', content)

    lab_tests = re.findall(r'\bLaboratory tests\b: (.+)', content)

    drugs = re.findall(r'\bdrugs\b: (.+)', content)

    treatments = re.findall(r'\btreatment\b: (.+)', content)

    causes = re.findall(r'\bcauses\b: (.+)', content)

    complications = re.findall(r'\bComplications\b: (.+)', content)

    risk_factors = re.findall(r'\bRisk factors\b: (.+)', content)

    pathophysiology = re.findall(r'\bPathophysiology\b: (.+)', content)

    return {
        'symptoms': symptoms,
        'signs': signs,
        'lab_tests': lab_tests,
        'drugs': drugs,
        'treatments': treatments,
        'causes': causes,
        'complications': complications,
        'risk_factors': risk_factors,
        'pathophysiology': pathophysiology
    }

# test
# disease_info = get_disease_info('Diabetes_mellitus_type_2')
# print(disease_info)

# icd9_dict = {
#     '250.00': 'Diabetes_mellitus_type_2',
#     # ...
# }

def get_icd9_info(icd9_dict):
    disease_info_dict = {}
    for icd9, disease_name in icd9_dict.items():
        disease_info = get_disease_info(disease_name)
        disease_info_dict[icd9] = disease_info
    return disease_info_dict