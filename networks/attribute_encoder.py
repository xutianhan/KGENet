import sys
sys.path.append('/')
import torch.nn as nn
from collections import defaultdict
from transformers import AutoTokenizer, AutoModel
import torch as th

class AttributeEncoder():
    def __init__(self, model_name):
        # 加载 ClinicalBERT 模型和分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)


    # 加载KG的文本属性描述
    def load_labels(self, label_attr_file):
        attribute_dict = defaultdict(str)
        with open(label_attr_file, 'r') as f1:
            for line in f1:
                line = line.strip()
                array = line.split('\t')
                if len(array) < 2:
                    continue
                icd_code = array[0]
                attribute_text = array[1]
                attribute_dict[icd_code] = attribute_text
        return attribute_dict


    def compute_attribute_embedding(self, label_attribute):
        # 对文本进行编码
        inputs = self.tokenizer(label_attribute, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
        # 使用模型获取输出
        with th.no_grad():
            outputs = self.model(**inputs)
        # 获取 BERT 嵌入
        bert_embedding = outputs.last_hidden_state
        attr_embedding, _ = th.max(bert_embedding, dim=1)
        return attr_embedding


    def init_all_label_embeddings(self, textfile):
        attribute_dict = self.load_labels(textfile)
        print("label count:", len(attribute_dict))
        embedding_list = []
        for icd_code, attribute_text in attribute_dict.items():
            attr_embedding = self.compute_attribute_embedding(attribute_text)
            # print(attr_embedding.shape)
            embedding_list.append(attr_embedding)
        W = th.cat(embedding_list, dim=0)
        # print(W.shape)
        label_embeddings = nn.Embedding.from_pretrained(W, freeze=True)
        print(label_embeddings.weight.shape)
        return label_embeddings


if __name__ == "__main__":
    print('start!')
    model_name = "emilyalsentzer/Bio_ClinicalBERT"
    attr_file = '/Users/guyixun/Documents/PHD/healthcare-code/ICD-coding-baseline/mimicdata/icd_knowledge/core-attribute/50_attribute_clean.txt'
    encoder = AttributeEncoder(model_name)
    embeddings = encoder.init_all_label_embeddings(attr_file)
    print('end!')
