import os
from tqdm import tqdm
import re
from random import shuffle

def line_reader(filename):
    with open(filename, "r", encoding="utf-8") as f:
        line = f.readline()
        while line:
            yield line
            line = f.readline()
    return

class UMLSDataLoader:
    def __init__(self, umls_path, source_range=None, lang_range=['ENG'], only_load_dict=False):
        self.umls_path = umls_path
        self.source_range = source_range
        self.lang_range = lang_range
        self._load_umls_data()

    def _load_umls_data(self):
        self._detect_type()
        reader = line_reader(os.path.join(self.umls_path, "MRCONSO." + self.umls_type))
        self.cui_to_str = {}
        self.str_to_cui = {}
        self.code_to_cui = {}
        read_count = 0
        for line in tqdm(reader, ascii=True):
            if self.umls_type == "txt":
                l = [t.replace("\"", "") for t in line.split(",")]
            else:
                l = line.strip().split("|")
            cui = l[0]
            lang = l[1]
            lui = l[3]
            source = l[11]
            code = l[13]
            string = l[14]

            if source == "ICD9CM":
                self.code_to_cui[code] = cui

            if (self.source_range is None or source in self.source_range) and (
                    self.lang_range is None or lang in self.lang_range):
                read_count += 1
                self.str_to_cui[string] = cui
                self.str_to_cui[string.lower()] = cui
                clean_string = self._clean(string, clean_bracket=False)
                self.str_to_cui[clean_string] = cui

                if cui not in self.cui_to_str:
                    self.cui_to_str[cui] = set()
                self.cui_to_str[cui].update([string.lower()])
                self.cui_to_str[cui].update([clean_string])

        self.cui_list = list(self.cui_to_str.keys())
        shuffle(self.cui_list)
        self.cui_count = len(self.cui_list)

        print("CUI count:", self.cui_count)
        print("str_to_cui count:", len(self.str_to_cui))
        print("MRCONSO count:", read_count)

    def _detect_type(self):
        if os.path.exists(os.path.join(self.umls_path, "MRCONSO.RRF")):
            self.umls_type = "RRF"
        else:
            self.umls_type = "txt"

    def _clean(self, term, lower=True, clean_NOS=True, clean_bracket=True, clean_dash=True):
        term = " " + term + " "
        if lower:
            term = term.lower()
        if clean_NOS:
            term = term.replace(" NOS ", " ").replace(" nos ", " ")
        if clean_bracket:
            term = re.sub(u"\\(.*?\\)", "", term)
        if clean_dash:
            term = term.replace("-", " ")
        term = " ".join([w for w in term.split() if w])
        return term

    def icd_str(self, icd):
        if icd in self.code_to_cui:
            cui = self.code_to_cui[icd]
            str_list = self.cui_to_str[cui]
            str_list = [w for w in str_list if len(w.split()) >= 2 or len(w) >= 7]
            return list(str_list)
        return []
