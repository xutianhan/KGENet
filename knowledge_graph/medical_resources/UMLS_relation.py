import os
from tqdm import tqdm

class UMLSRelations:
    def __init__(self, umls_path):
        self.umls_path = umls_path
        self.load()

    def load(self):
        self.code_relations = {}
        mrrel_file_path = os.path.join(self.umls_path, "MRREL.RRF")
        if os.path.exists(mrrel_file_path):
            with open(mrrel_file_path, "r", encoding="utf-8") as f:
                for line in tqdm(f, ascii=True):
                    parts = line.strip().split("|")
                    if len(parts) >= 10:
                        cui1 = parts[0]
                        cui2 = parts[4]
                        relation = parts[3]
                        if relation == "RN":
                            relation_type = parts[7]
                            if cui1 not in self.code_relations:
                                self.code_relations[cui1] = {}
                            if relation_type not in self.code_relations[cui1]:
                                self.code_relations[cui1][relation_type] = set()
                            self.code_relations[cui1][relation_type].add(cui2)

    def get_relations(self, icd9_code):
        if icd9_code in self.code_relations:
            return self.code_relations[icd9_code]
        else:
            return {}

# Example
umls = UMLSRelations("/path/to/umls")
icd9_code = "123.4"  # Example ICD9 code
relations = umls.get_relations(icd9_code)
print("Relations for ICD9 code", icd9_code)
print(relations)
