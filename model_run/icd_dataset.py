from torch.utils.data import Dataset
import torch as th
from sklearn.preprocessing import MultiLabelBinarizer
import os
import numpy as np

class ICD_Dataset(Dataset):
    def __init__(self, hadm_ids, texts, labels, batch_size, data_setting, class_order_path):
        self.hadm_ids = hadm_ids
        self.texts = texts
        self.labels = labels
        self.batch_size = batch_size
        self.mlb = self.load_class_order(data_setting, class_order_path)

    def __len__(self):
        return len(self.texts) // self.batch_size


    def __getitem__(self, index):

        start_index = index * self.batch_size
        end_index = (index + 1) * self.batch_size

        hadm_ids_batch = self.hadm_ids[start_index:end_index]
        texts_batch = self.texts[start_index:end_index]
        labels_batch = self.labels[start_index:end_index]

        hadm_ids_tensor = th.tensor(hadm_ids_batch)
        texts_tensor = th.tensor(texts_batch, dtype=th.long)

        # Transform labels to multi-hot vectors
        labels_multi_hot = self.mlb.transform(labels_batch)

        return {'hadm_id': hadm_ids_tensor, 'text': texts_tensor,
                'targets': th.tensor(labels_multi_hot, dtype=th.float)}


    def load_class_order(self, data_setting, class_order_path):
        # CLASS_ORDER_PATH = "/root/autodl-tmp/KGENet/icd_knowledge"
        class_order_file = f'{class_order_path}/{data_setting}_class_order.npy'
        if not os.path.exists(class_order_file):
            raise FileNotFoundError(f"Class order file '{class_order_file}' not found.")
        class_order = np.load(class_order_file, allow_pickle=True)
        mlb = MultiLabelBinarizer(classes=class_order)
        mlb.fit([])  # Fit an empty array to ensure consistent label ordering
        return mlb