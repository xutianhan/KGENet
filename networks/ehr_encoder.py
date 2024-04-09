import sys
sys.path.append('/')
from transformers import LongformerModel
from transformers import LongformerTokenizerFast
import torch as th

class EHREncoder():
    def __init__(self, model_name):
        # 加载 Clinical-Longformer 模型和分词器
        self.tokenizer = LongformerTokenizerFast.from_pretrained(model_name)
        self.model = LongformerModel.from_pretrained(model_name)


    # 加载KG的文本属性描述
    def load_data(self, train_file):
        ehr_list = []
        with open(train_file, 'r') as f1:
            for line in f1:
                line = line.strip()
                array = line.split('\t')
                if len(array) < 4:
                    continue
                ehr_text = array[2]
                labels = array[3]
                data = (ehr_text, labels)
                ehr_list.append(data)
        return ehr_list


    def compute_ehr_embedding(self, input_ids):
        # 将 input_ids 转换为 torch.Tensor 类型
        input_ids_tensor = th.tensor(input_ids)
        # 使用模型计算 embeddings
        outputs = self.model(input_ids_tensor)
        # outputs 是一个元组，第一个元素是 sequence output
        sequence_output = outputs[0]
        return sequence_output

    # def batch_ehr_embeddings(self, batch_input_ids):
    #     embedding_list = []
    #     for input_ids in batch_input_ids:
    #         ehr_embedding = self.compute_ehr_embedding(input_ids)
    #         embedding_list.append(ehr_embedding)
    #     # 使用 stack 而不是 cat，以创建一个新的维度
    #     batch_ehr_embeddings = th.stack(embedding_list, dim=0)
    #     return batch_ehr_embeddings

    def text_to_sequence(self, text):
        # 使用 tokenizer 对文本进行编码
        encoded_text = self.tokenizer(text, return_tensors="pt", padding="max_length", truncation=True,
                                      max_length=4096)
        # 提取编码后的整数序列
        sequence = encoded_text.input_ids.squeeze(0)  # 去除多余的维度
        return sequence

