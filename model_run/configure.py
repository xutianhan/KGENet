import json

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def update_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def get_config(self):
        return self.config

# 创建配置实例
config = Config('config.json')

# 数据设置
config.update_config('data_setting', '50')
config.update_config('batch_size', 32)
config.update_config('max_len', 4096)

# 模型设置
config.update_config('label_emb_model_name', 'emilyalsentzer/Bio_ClinicalBERT')
config.update_config('ehr_emb_model_name', 'yikuan8/Clinical-Longformer')
config.update_config('label_attr_file', 'label_attributes.txt')
config.update_config('embedding_size', 768)
config.update_config('mid_size', 256)
config.update_config('num_classes', 50)
config.update_config('label_graph', 'label_graph.txt')
config.update_config('time_step', 3)

# 训练设置
config.update_config('learning_rate', 0.001)
config.update_config('num_epoch', 8)

# 日志设置
config.update_config('log', 'info')

# 随机种子设置
config.update_config('random_seed', 42)
