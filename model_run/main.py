import sys
sys.path.append("../")
import logging
import numpy as np
from collections import OrderedDict, namedtuple
from itertools import product
from data import prepare_datasets
from trainer import train
import random
import os
import torch as th
from networks.KGENet import KGENet
import configure

def get_hyper_params_combinations(args):
    params = OrderedDict(
        learning_rate=args['learning_rate'],
        num_epoch=args['num_epoch']
    )

    HyperParams = namedtuple('HyperParams', params.keys())
    hyper_params_list = []
    for v in product(*params.values()):
        hyper_params_list.append(HyperParams(*v))
    return hyper_params_list

def run(args, device):
    train_set, dev_set, test_set = prepare_datasets(args['data_setting'], args['batch_size'])
    logging.info(f'Training labels are: {train_set["labels"]}\n')

    for hyper_params in get_hyper_params_combinations(args):
        # 创建模型实例
        model = KGENet(
            label_emb_model_name=args['label_emb_model_name'],
            ehr_emb_model_name=args['ehr_emb_model_name'],
            label_attr_file=args['label_attr_file'],
            embedding_size=args['embedding_size'],
            mid_size=args['mid_size'],
            num_classes=args['num_classes'],
            label_graph=args['label_graph'],
            time_step=args['time_step']
        )

        if model:
            model.to(device)
            logging.info(f"Training with: {hyper_params}")
            train(model, train_set, dev_set, test_set, hyper_params, args['batch_size'], device)


if __name__ == "__main__":
    config_args = configure.config.get_config()
    if not os.path.exists('../results'):
        os.makedirs('../results')
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename='../results/model.log', filemode='w', format=FORMAT, level=getattr(logging, config_args['log'].upper()))
    logging.info(f'{config_args}\n')
    use_cuda = th.cuda.is_available()
    device = th.device("cuda" if use_cuda else "cpu")
    # 设置随机数种子，保证同样的种子结果相同
    random.seed(config_args['random_seed'])
    np.random.seed(config_args['random_seed'])
    th.manual_seed(config_args['random_seed'])
    if use_cuda:
        th.cuda.manual_seed_all(config_args['random_seed'])
    run(config_args, device)
