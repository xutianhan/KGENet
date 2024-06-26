from torch.utils.data import Dataset
import torch as th
from sklearn.preprocessing import MultiLabelBinarizer
import os
import numpy as np
from networks.ehr_encoder import EHREncoder

class ICD_Dataset(Dataset):
    def __init__(self, hadm_ids, texts, labels, batch_size, data_setting, class_order_path):
        self.hadm_ids = hadm_ids
        self.texts = texts
        self.labels = labels
        self.batch_size = batch_size
        self.mlb = self.load_class_order(data_setting, class_order_path)
        self.ehr_encoder = EHREncoder("yikuan8/Clinical-Longformer")

    def __len__(self):
        return len(self.texts) // self.batch_size


    def __getitem__(self, index):
        text = self.texts[index]
        label = self.labels[index]

        text_seq = self.ehr_encoder.text_to_sequence(text)

        return {'text': text_seq,
                'targets': th.tensor(label, dtype=th.float)}

    def load_class_order(self, data_setting, class_order_path):
        class_order_file = f'{class_order_path}/{data_setting}_class_order.npy'
        if not os.path.exists(class_order_file):
            raise FileNotFoundError(f"Class order file '{class_order_file}' not found.")
        class_order = np.load(class_order_file, allow_pickle=True)
        # print("Loaded class order:", class_order)
        mlb = MultiLabelBinarizer(classes=class_order)
        mlb.fit([])  # Fit an empty array to ensure consistent label ordering
        return mlb
