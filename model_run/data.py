import logging
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import MultiLabelBinarizer
from model_run.icd_dataset import ICD_Dataset


DATA_DIR = '../train-data'
CLASS_ORDER_PATH = "../knowledge-data"


def load_dataset(data_setting, batch_size, splited_data):
    data = pd.read_csv(f'{DATA_DIR}/{splited_data}_{data_setting}_entities.csv', dtype={'LENGTH': int})
    data['LABELS'] = data['LABELS'].apply(lambda x: str(x).split(';'))
    code_counts = list(data['LABELS'].str.len())
    avg_code_counts = sum(code_counts) / len(code_counts)
    logging.info(f'In {splited_data} set, average code counts per ehr: {avg_code_counts}')

    # 第一次实例化class保存顺序，以后使用均按照这个顺序
    class_order_file = f'{CLASS_ORDER_PATH}/{data_setting}_class_order.npy'
    if not os.path.exists(class_order_file):
        mlb = MultiLabelBinarizer()
        mlb.fit(data['LABELS'])
        np.save(class_order_file, mlb.classes_)
    else:
        mlb = MultiLabelBinarizer(classes=np.load(class_order_file, allow_pickle=True))

    if mlb.classes_[-1] == 'nan':
        mlb.classes_ = mlb.classes_[:-1]

    print(f'Final number of labels/codes: {len(mlb.classes_)}')

    for label in mlb.classes_:
        data[label] = mlb.transform(data['LABELS'])[:, mlb.classes_ == label]

    data.drop(['LABELS', 'LENGTH'], axis=1, inplace=True)

    item_count = (len(data) // batch_size) * batch_size
    logging.info(f'{splited_data} set true item count: {item_count}\n\n')
    print(f'{splited_data} set true item count: {item_count}\n\n')

    return {
        'hadm_ids': data['HADM_ID'].values[:item_count],
        'texts': data['TEXT'].values[:item_count],
        'targets': data[mlb.classes_].values[:item_count],
        'labels': mlb.classes_,
        'label_freq': data[mlb.classes_].sum(axis=0)
    }


def verify_datasets(data_setting, batch_size):
    train_raw = load_dataset(data_setting, batch_size, splited_data='train')
    dev_raw = load_dataset(data_setting, batch_size, splited_data='dev')
    test_raw = load_dataset(data_setting, batch_size, splited_data='test')

    if not np.array_equal(train_raw['labels'], dev_raw['labels']) or not np.array_equal(dev_raw['labels'], test_raw['labels']):
        raise ValueError("Train dev test labels don't match!")

    return train_raw, dev_raw, test_raw


def prepare_datasets(data_setting, batch_size):
    train_data, dev_data, test_data = verify_datasets(data_setting, batch_size)
    train_set = ICD_Dataset(train_data['hadm_ids'], train_data['texts'], train_data['targets'], batch_size, data_setting, CLASS_ORDER_PATH)
    dev_set = ICD_Dataset(dev_data['hadm_ids'], dev_data['texts'], dev_data['targets'], batch_size, data_setting, CLASS_ORDER_PATH)
    test_set = ICD_Dataset(test_data['hadm_ids'], test_data['texts'], test_data['targets'], batch_size, data_setting, CLASS_ORDER_PATH)
    return train_set, dev_set, test_set
